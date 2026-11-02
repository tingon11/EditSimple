# EditSimple — montaggio video per presentazioni.  Copyright (C) 2026 Andrea Cumini <andrea@osintinfo.net>
# SPDX-License-Identifier: GPL-3.0-only
# GNU GPL v3 con termini aggiuntivi (attribuzione dell'autore): vedi LICENSE e NOTICE.
"""Ricerca, download e aggiornamento di ffmpeg (e del modello VitTrack) nella cartella tools/.

ffmpeg e' un programma separato, con la propria licenza: non viene incluso
nel programma ne' nell'eseguibile. Viene cercato, nell'ordine, in
tools/ffmpeg/ffmpeg.exe accanto al programma e nel PATH di sistema. Il
download prende il build Windows "release essentials" di gyan.dev, quello
indicato dal sito ufficiale di FFmpeg (https://ffmpeg.org/download.html):
dallo zip si tengono solo ffmpeg.exe, LICENSE e README. Nessuna installazione
globale, nessuna modifica al PATH: tutto resta dentro tools/.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import __version__, procs
from .config import APP_DIR
from .i18n import tr

TOOLS_DIR = APP_DIR / "tools"
FFMPEG_DIR = TOOLS_DIR / "ffmpeg"
FFMPEG_EXE = FFMPEG_DIR / ("ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
VERSION_FILE = FFMPEG_DIR / "VERSION"

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_SHA256_URL = FFMPEG_URL + ".sha256"          # impronta pubblicata da gyan.dev accanto all'archivio
FFMPEG_VERSION_URL = "https://www.gyan.dev/ffmpeg/builds/release-version"
FFMPEG_PAGE = "https://www.gyan.dev/ffmpeg/builds/"
KEEP_FILES = ("LICENSE", "README.txt")

USER_AGENT = f"EditSimple/{__version__}"

ProgressCb = Callable[[str, int, int], None]


class ToolsError(RuntimeError):
    """Errore durante la verifica o il download di ffmpeg."""


class Cancelled(Exception):
    """Download interrotto dall'utente."""


@dataclass
class Status:
    path: Path | None
    source: str = ""      # "tools", "path" o ""
    version: str = ""

    @property
    def present(self) -> bool:
        return self.path is not None


def find() -> tuple[Path | None, str]:
    """Percorso di ffmpeg e da dove viene: tools/ oppure PATH."""
    if FFMPEG_EXE.is_file():
        return FFMPEG_EXE, "tools"
    found = shutil.which("ffmpeg")
    if found:
        return Path(found), "path"
    return None, ""


def version_of(exe: Path) -> str:
    """Versione stampata da `ffmpeg -version` (es. "7.1-essentials_build-www.gyan.dev")."""
    try:
        result = procs.run([str(exe), "-version"], timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    first = result.stdout.decode("utf-8", "replace").splitlines()[:1]
    if not first or not first[0].startswith("ffmpeg version "):
        return ""
    return first[0].split()[2]


def status() -> Status:
    """Stato corrente: dove sta ffmpeg e che versione e' (la lettura avvia un processo)."""
    path, source = find()
    if path is None:
        return Status(None)
    return Status(path, source, version_of(path))


def installed_release() -> str:
    """Versione di release scritta in tools/ffmpeg/VERSION dall'ultimo download ("" se non c'e')."""
    try:
        return VERSION_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


# ----------------------------------------------------------------- download

def _open(url: str, timeout: float = 30.0):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(request, timeout=timeout)


def latest_release() -> str:
    """Ultima versione di release pubblicata da gyan.dev (es. "7.1")."""
    try:
        with _open(FFMPEG_VERSION_URL) as response:
            text = response.read(200).decode("utf-8", "replace").strip()
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise ToolsError(tr("Impossibile controllare l'ultima versione di ffmpeg: {error}").format(error=exc)) from exc
    if not text or len(text) > 40 or "\n" in text:
        raise ToolsError(tr("Risposta inattesa dal sito di download di ffmpeg."))
    return text


def ffmpeg_sha256() -> str:
    """L'impronta SHA-256 dell'archivio pubblicata da gyan.dev (64 cifre esadecimali)."""
    try:
        with _open(FFMPEG_SHA256_URL) as response:
            text = response.read(400).decode("ascii", "replace")
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise ToolsError(tr("Impossibile leggere l'impronta SHA-256 di ffmpeg: {error}").format(error=exc)) from exc
    match = re.search(r"\b[0-9a-fA-F]{64}\b", text)
    if match is None:
        raise ToolsError(tr("Impronta SHA-256 di ffmpeg non valida."))
    return match.group(0).lower()


def _download(url: str, target: Path, label: str, progress: ProgressCb | None,
              cancel: threading.Event | None) -> None:
    """Scarica un file mostrando l'avanzamento; si ferma se `cancel` viene impostato."""
    try:
        with _open(url, timeout=60) as response:
            total = int(response.headers.get("Content-Length") or 0)
            done = 0
            with target.open("wb") as handle:
                while True:
                    if cancel is not None and cancel.is_set():
                        raise Cancelled()
                    block = response.read(256 * 1024)
                    if not block:
                        break
                    handle.write(block)
                    done += len(block)
                    if progress:
                        progress(tr("Download di {name}").format(name=label), done, total)
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise ToolsError(tr("Download di {name} fallito: {error}").format(name=label, error=exc)) from exc


def _extract_wanted(archive: Path, destination: Path) -> None:
    """Prende dallo zip solo ffmpeg.exe, LICENSE e README, rifiutando percorsi sospetti."""
    destination.mkdir(parents=True, exist_ok=True)
    root = destination.resolve()
    wanted = {FFMPEG_EXE.name: "bin/" + FFMPEG_EXE.name}
    for name in KEEP_FILES:
        wanted[name] = name
    found: set[str] = set()
    try:
        with zipfile.ZipFile(archive) as zf:
            for member in zf.namelist():
                if not (root / member).resolve().is_relative_to(root):
                    raise ToolsError(tr("Archivio non valido: percorso sospetto '{path}'.").format(path=member))
                parts = member.replace("\\", "/").split("/")
                for out_name, tail in wanted.items():
                    if "/".join(parts[-tail.count("/") - 1:]) == tail and out_name not in found:
                        with zf.open(member) as src, (destination / out_name).open("wb") as dst:
                            shutil.copyfileobj(src, dst, 1024 * 1024)
                        found.add(out_name)
    except zipfile.BadZipFile as exc:
        raise ToolsError(tr("Il file scaricato non e' un archivio zip valido.")) from exc
    if FFMPEG_EXE.name not in found:
        raise ToolsError(tr("Il pacchetto scaricato non contiene {file}.").format(file=FFMPEG_EXE.name))


def _replace_dir(source: Path, target: Path) -> None:
    """Sostituisce la cartella di destinazione con il contenuto scaricato."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        backup = target.with_name(target.name + ".old")
        shutil.rmtree(backup, ignore_errors=True)
        try:
            target.rename(backup)
        except OSError as exc:
            raise ToolsError(tr("Impossibile aggiornare '{folder}': file in uso. "
                                "Aspetta la fine dell'esportazione e riprova.").format(folder=target.name)) from exc
        shutil.rmtree(backup, ignore_errors=True)
    shutil.move(str(source), str(target))


def install(progress: ProgressCb | None = None, cancel: threading.Event | None = None) -> Path:
    """Scarica il build ufficiale e lascia ffmpeg.exe in tools/ffmpeg/. Restituisce l'eseguibile."""
    if sys.platform != "win32":
        raise ToolsError(tr("Il download automatico e' disponibile solo su Windows: installa ffmpeg "
                            "con il gestore di pacchetti del sistema."))
    release = ""
    try:
        release = latest_release()
    except ToolsError:
        pass  # la versione serve solo per i controlli futuri: il download puo' procedere lo stesso
    with tempfile.TemporaryDirectory(prefix="editsimple-") as tmp:
        tmp_dir = Path(tmp)
        archive = tmp_dir / "ffmpeg.zip"
        expected = ffmpeg_sha256()              # prima del download: senza impronta non si installa nulla
        _download(FFMPEG_URL, archive, "ffmpeg", progress, cancel)
        if _sha256(archive) != expected:
            # l'archivio puo' essere cambiato fra la lettura dell'impronta e il download: si riprova una volta
            expected = ffmpeg_sha256()
            if _sha256(archive) != expected:
                raise ToolsError(tr("L'archivio di ffmpeg scaricato non corrisponde all'impronta SHA-256 "
                                    "pubblicata: non viene installato."))
        if progress:
            progress(tr("Estrazione di ffmpeg"), 0, 0)
        out = tmp_dir / "ffmpeg"
        _extract_wanted(archive, out)
        if not version_of(out / FFMPEG_EXE.name):
            raise ToolsError(tr("L'ffmpeg scaricato non si avvia su questo PC."))
        if release:
            (out / VERSION_FILE.name).write_text(release + "\n", encoding="utf-8")
        _replace_dir(out, FFMPEG_DIR)
    if not FFMPEG_EXE.is_file():
        raise ToolsError(tr("{file} manca dopo l'estrazione.").format(file=FFMPEG_EXE.name))
    return FFMPEG_EXE


# ----------------------------------------------------------------- VitTrack (inseguimento)
#
# Modello di inseguimento VitTrack del repository ufficiale opencv_zoo (licenza Apache 2.0,
# compatibile con la GPL 3). Come ffmpeg non sta nel programma ne' nell'eseguibile: si scarica in
# tools/vittrack/ insieme alla sua licenza. Il file viene controllato con l'impronta SHA-256.

VIT_DIR = TOOLS_DIR / "vittrack"
VIT_MODEL = VIT_DIR / "object_tracking_vittrack_2023sep.onnx"
# URL fissati al commit di opencv_zoo che contiene esattamente questo modello: un aggiornamento del file
# su main non rompe il download (l'impronta qui sotto e' di quella versione)
VIT_COMMIT = "fef72f8fa7c52eaf116d3df358d24e6e959ada0e"
VIT_URL = (f"https://github.com/opencv/opencv_zoo/raw/{VIT_COMMIT}/models/object_tracking_vittrack/"
           "object_tracking_vittrack_2023sep.onnx")
VIT_LICENSE_URL = (f"https://raw.githubusercontent.com/opencv/opencv_zoo/{VIT_COMMIT}/models/"
                   "object_tracking_vittrack/LICENSE")
VIT_PAGE = "https://github.com/opencv/opencv_zoo/tree/main/models/object_tracking_vittrack"
VIT_SHA256 = "2990f0b7cd44d92afa48cd97db6de7be113fc1d9594fddb74e2725c10478e91d"


def vit_model() -> Path | None:
    """Il modello VitTrack, se e' stato scaricato (None altrimenti)."""
    return VIT_MODEL if VIT_MODEL.is_file() else None


def _sha256(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def install_vit(progress: ProgressCb | None = None, cancel: threading.Event | None = None) -> Path:
    """Scarica il modello VitTrack e la sua licenza in tools/vittrack/."""
    with tempfile.TemporaryDirectory(prefix="editsimple-") as tmp:
        out = Path(tmp) / "vittrack"
        out.mkdir()
        model = out / VIT_MODEL.name
        _download(VIT_URL, model, "VitTrack", progress, cancel)
        if _sha256(model) != VIT_SHA256:
            raise ToolsError(tr("Il modello scaricato non corrisponde a quello atteso (impronta SHA-256 diversa)."))
        _download(VIT_LICENSE_URL, out / "LICENSE", tr("licenza di VitTrack"), progress, cancel)
        (out / "README.txt").write_text(
            "VitTrack (vision transformer tracker), modello del repository opencv_zoo:\n"
            f"{VIT_PAGE}\nLicenza Apache 2.0 (vedi LICENSE). Usato da EditSimple per l'inseguimento.\n",
            encoding="utf-8")
        try:
            import cv2
            params = cv2.TrackerVit_Params()
            params.net = str(model)
            cv2.TrackerVit_create(params)
        except (cv2.error, AttributeError) as exc:
            raise ToolsError(tr("OpenCV non riesce a caricare il modello: {error}").format(error=exc)) from exc
        _replace_dir(out, VIT_DIR)
    return VIT_MODEL
