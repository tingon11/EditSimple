# EditSimple — montaggio video per presentazioni.  Copyright (C) 2026 Andrea Cumini <andrea@osintinfo.net>
# SPDX-License-Identifier: GPL-3.0-only
# GNU GPL v3 con termini aggiuntivi (attribuzione dell'autore): vedi LICENSE e NOTICE.
"""Immagine con didascalia per Word (pagina Immagini, pulsante Word).

La didascalia e' su una riga: "Figura 1 : testo del foglio. 1) nota, 2) nota,
A) nota", dove 1 e' il numero automatico di Word; testo e note sono facoltativi.

Il modo sicuro e' `insert`: con l'automazione di Word (uno script PowerShell,
nessuna dipendenza in piu') l'immagine va nel documento aperto, dove c'e' il
cursore, e la didascalia la crea Word stesso con Inserisci didascalia: stile
Didascalia e numero giusti qualunque siano le impostazioni di Word.

Se Word non c'e' o non risponde resta la copia negli appunti (`rtf`): un piccolo
documento RTF con l'immagine e il paragrafo in stile "caption" con il campo SEQ.
Incollando, pero', Word lo tiene come didascalia solo se "Incolla da altri
programmi" usa gli stili di destinazione; con "Unisci formattazione" diventa testo.
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image

MAX_SIDE = 2000                 # pixel: abbastanza per la stampa, l'RTF resta leggero
WIDTH_TWIPS = 9000              # circa 16 cm, la larghezza utile di una pagina A4
MAX_HEIGHT_TWIPS = 12000        # circa 21 cm


def _escape(text: str) -> str:
    """Testo per l'RTF: caratteri speciali protetti, quelli non ASCII come \\uN?."""
    out = []
    for ch in text:
        if ch in "\\{}":
            out.append("\\" + ch)
        elif ch == "\n":
            out.append("\\line ")
        elif ord(ch) < 128:
            out.append(ch)
        else:
            for unit in _utf16(ch):
                out.append(f"\\u{unit - 65536 if unit > 32767 else unit}?")
    return "".join(out)


def _utf16(ch: str) -> list[int]:
    data = ch.encode("utf-16-le")
    return [int.from_bytes(data[i:i + 2], "little") for i in range(0, len(data), 2)]


def rtf(image: Image.Image, label: str, lines: list[str], intro: str = "") -> bytes:
    """Immagine e didascalia "label N : voce, voce" (N e' il numero automatico di Word)."""
    image = image.convert("RGB")
    scale = min(1.0, MAX_SIDE / max(image.size))
    if scale < 1.0:
        image = image.resize((max(1, int(image.width * scale)), max(1, int(image.height * scale))), Image.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=90)
    goal_w = WIDTH_TWIPS
    goal_h = int(goal_w * image.height / image.width)
    if goal_h > MAX_HEIGHT_TWIPS:
        goal_w, goal_h = int(goal_w * MAX_HEIGHT_TWIPS / goal_h), MAX_HEIGHT_TWIPS
    data = buffer.getvalue().hex()
    data = "\n".join(data[i:i + 128] for i in range(0, len(data), 128))
    seq = _escape(label).replace(" ", "_")
    caption = (f"{_escape(label)} {{\\field{{\\*\\fldinst SEQ {seq} \\\\* ARABIC}}{{\\fldrslt 1}}}}"
               + _escape(caption_title(lines, intro)))
    doc = ("{\\rtf1\\ansi\\ansicpg1252\\deff0\\uc1"
           "{\\fonttbl{\\f0\\fswiss Calibri;}}"
           "{\\stylesheet{\\s0\\f0 Normal;}{\\s15\\sbasedon0\\snext0 caption;}}\n"
           "\\pard\\plain\\s0\\f0\\keepn "
           f"{{\\pict\\jpegblip\\picw{image.width}\\pich{image.height}\\picwgoal{goal_w}\\pichgoal{goal_h}\n{data}}}"
           "\\par\n"
           f"\\pard\\plain\\s15\\f0 {caption}\\par\n}}")
    return doc.encode("ascii")


def text(label: str, lines: list[str], intro: str = "") -> str:
    """La didascalia come testo semplice, per i programmi che non leggono l'RTF (senza il numero di Word)."""
    return caption_title(lines, intro).lstrip(" :") or label


# ----------------------------------------------------------- inserimento diretto nel documento aperto

WORD_TIMEOUT = 90               # secondi: aprire Word la prima volta puo' essere lento

# Solo caratteri ASCII: PowerShell 5 legge gli script senza BOM con la codifica di sistema.
# I dati (immagine, etichetta, titolo) arrivano da un file JSON in UTF-8.
_SCRIPT = r"""
param([string]$Data)
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [Text.Encoding]::UTF8
try {
    $d = Get-Content -Raw -Encoding UTF8 -LiteralPath $Data | ConvertFrom-Json
    try { $word = [Runtime.InteropServices.Marshal]::GetActiveObject('Word.Application') } catch { $word = $null }
    if ($null -eq $word) { $word = New-Object -ComObject Word.Application }
    $word.Visible = $true
    if ($word.Documents.Count -eq 0) { $doc = $word.Documents.Add() } else { $doc = $word.ActiveDocument }
    $sel = $word.Selection
    $sel.Collapse(0)
    if ($sel.Start -ne $sel.Paragraphs.Item(1).Range.Start) { $sel.TypeParagraph() }
    $shape = $sel.InlineShapes.AddPicture($d.image, $false, $true)
    $sel.SetRange($shape.Range.End, $shape.Range.End)
    $sel.TypeParagraph()
    $page = $doc.PageSetup
    $usable = $page.PageWidth - $page.LeftMargin - $page.RightMargin
    $shape.LockAspectRatio = -1
    $shape.Width = [Math]::Min($usable, [double]$d.width)
    $shape.Range.ParagraphFormat.KeepWithNext = -1
    $found = $false
    foreach ($l in $word.CaptionLabels) { if ($l.Name -eq $d.label) { $found = $true } }
    if (-not $found) { $word.CaptionLabels.Add($d.label) | Out-Null }
    $shape.Select()
    $word.Selection.InsertCaption($d.label, $d.title, '', 1)
    $caption = $shape.Range.Paragraphs.Item(1).Next(1)
    $word.Selection.SetRange($caption.Range.End, $caption.Range.End)
    try { $word.Activate() } catch { }
    $text = ($caption.Range.Text -replace "[\r\v\a]", '').Trim()
    [Console]::Out.Write("OK`t" + $doc.Name + "`t" + $text)
} catch {
    [Console]::Out.Write("ERR`t" + $_.Exception.Message)
}
"""


def caption_title(lines: list[str], intro: str = "") -> str:
    """Il testo dopo "Figura N": " : testo. 1) nota, 2) nota" (vuoto se non c'e' ne' testo ne' note)."""
    intro = " ".join(intro.split())
    notes = ", ".join(lines)
    if intro and notes:
        body = intro + (" " if intro[-1] in ".!?:;,-" else ". ") + notes
    else:
        body = intro or notes
    return " : " + body if body else ""


def insert(image: Image.Image, label: str, lines: list[str], intro: str = "") -> tuple[bool, str, str]:
    """Inserisce l'immagine e la sua didascalia nel documento Word aperto, dove c'e' il cursore.

    Restituisce (riuscito, nome del documento, testo della didascalia) oppure (False, "", errore).
    Blocca finche' Word non ha finito: va chiamata da un thread di lavoro.
    """
    if sys.platform != "win32":
        return False, "", "Word automation needs Windows"
    folder = tempfile.mkdtemp(prefix="editsimple_word_")
    try:
        picture = os.path.join(folder, "figura.png")
        image.convert("RGB").save(picture, "PNG")
        data = os.path.join(folder, "dati.json")
        with open(data, "w", encoding="utf-8") as fh:
            json.dump({"image": picture, "label": label, "title": caption_title(lines, intro),
                       "width": WIDTH_TWIPS / 20}, fh, ensure_ascii=False)
        script = os.path.join(folder, "inserisci.ps1")
        with open(script, "w", encoding="ascii") as fh:
            fh.write(_SCRIPT)
        try:
            done = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                                   "-File", script, "-Data", data], capture_output=True, timeout=WORD_TIMEOUT,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
        except (OSError, subprocess.TimeoutExpired) as exc:
            return False, "", str(exc)
        out = done.stdout.decode("utf-8", "replace").strip()
        if out.startswith("OK\t"):
            _ok, document, caption = (out.split("\t") + ["", ""])[:3]
            return True, document, caption
        error = out.split("\t", 1)[1] if out.startswith("ERR\t") else (done.stderr.decode("utf-8", "replace").strip()
                                                                       or out or f"exit {done.returncode}")
        return False, "", error
    finally:
        for name in os.listdir(folder):
            try:
                os.remove(os.path.join(folder, name))
            except OSError:
                pass
        try:
            os.rmdir(folder)
        except OSError:
            pass
