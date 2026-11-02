# EditSimple — montaggio video per presentazioni.  Copyright (C) 2026 Andrea Cumini <andrea@osintinfo.net>
# SPDX-License-Identifier: GPL-3.0-only
# GNU GPL v3 con termini aggiuntivi (attribuzione dell'autore): vedi LICENSE e NOTICE.
"""Tavola di immagini statiche da annotare (pagina Immagini).

Un foglio di misura fissa (il formato) diviso in riquadri secondo un layout
da 1 a 4 immagini. Ogni riquadro mostra un'immagine adattata al riquadro, che
si puo' ingrandire (`zoom`) e spostare (`cx`, `cy`: il punto dell'immagine, in
frazioni della sua larghezza e altezza, che sta al centro del riquadro). Le
annotazioni sono gli stessi effetti del video, fermi, in un Project usato solo
per tenerli: si disegnano sopra il foglio con overlays.compose.

Un'annotazione disegnata tutta dentro un'immagine le appartiene (`fx["cell"]` =
id del riquadro): le sue coordinate restano quelle del foglio (cosi' l'anteprima
le sposta e le ridimensiona come nel video), ma quando la vista di quel riquadro
cambia (ingrandimento, spostamento, layout, formato, spazio) vengono ricalcolate
perche' restino sullo stesso punto dell'immagine; e nel risultato restano
dentro il loro riquadro. Quelle a cavallo di due immagini, o fuori dalle
immagini (e il logo), sono del foglio: restano ferme e si vedono intere.

Freccia e collegamento uniscono due punti, anche su due immagini diverse: ogni
estremo segue la sua (`cell1`, `cell2`) e non si ritagliano mai.

Il progetto si salva in un file JSON leggibile, con accanto una cartella
"<nome>_file" che contiene le immagini dei riquadri (l'originale copiato com'e',
o in PNG se veniva dagli appunti), le immagini sopra il foglio e i loghi; nel
JSON i percorsi sono relativi, cosi' file e cartella si possono spostare insieme.
"""

from __future__ import annotations

import copy
import json
import os
import shutil
import uuid

from PIL import Image, ImageOps

from . import overlays
from .config import write_atomic
from .i18n import N_
from .project import Project

PROJECT_KIND = "editsimple-images"
PROJECT_VERSION = 1

# chiave -> (numero di immagini, nome, riquadri come (x, y, larghezza, altezza) in frazioni del foglio)
LAYOUTS: dict[str, tuple[int, str, list[tuple[float, float, float, float]]]] = {
    "1": (1, N_("Una immagine"), [(0, 0, 1, 1)]),
    "2h": (2, N_("Affiancate"), [(0, 0, .5, 1), (.5, 0, .5, 1)]),
    "2v": (2, N_("Una sopra l'altra"), [(0, 0, 1, .5), (0, .5, 1, .5)]),
    "3h": (3, N_("Tre in fila"), [(0, 0, 1 / 3, 1), (1 / 3, 0, 1 / 3, 1), (2 / 3, 0, 1 / 3, 1)]),
    "3v": (3, N_("Tre in colonna"), [(0, 0, 1, 1 / 3), (0, 1 / 3, 1, 1 / 3), (0, 2 / 3, 1, 1 / 3)]),
    "3l": (3, N_("Una grande a sinistra"), [(0, 0, .6, 1), (.6, 0, .4, .5), (.6, .5, .4, .5)]),
    "3t": (3, N_("Una grande sopra"), [(0, 0, 1, .6), (0, .6, .5, .4), (.5, .6, .5, .4)]),
    "4g": (4, N_("Griglia 2 x 2"), [(0, 0, .5, .5), (.5, 0, .5, .5), (0, .5, .5, .5), (.5, .5, .5, .5)]),
    "4h": (4, N_("Quattro in fila"), [(i / 4, 0, .25, 1) for i in range(4)]),
    "4l": (4, N_("Una grande a sinistra"), [(0, 0, .6, 1)] + [(.6, i / 3, .4, 1 / 3) for i in range(3)]),
    "4t": (4, N_("Una grande sopra"), [(0, 0, 1, .6)] + [(i / 3, .6, 1 / 3, .4) for i in range(3)]),
}

# formato del foglio -> (nome, larghezza, altezza)
FORMATS: dict[str, tuple[str, int, int]] = {
    "16:9": (N_("16:9 orizzontale"), 1920, 1080),
    "4:3": (N_("4:3"), 1600, 1200),
    "1:1": (N_("Quadrato"), 1200, 1200),
    "9:16": (N_("9:16 verticale"), 1080, 1920),
    "A4": (N_("A4 verticale"), 2480, 3508),
}

MIN_ZOOM = 0.2
MAX_ZOOM = 40.0


def new_cell() -> dict:
    return {"id": uuid.uuid4().hex[:8], "image": None, "zoom": 1.0, "cx": 0.5, "cy": 0.5, "name": ""}


POINT_X = ("x", "x1", "x2")          # coordinate che si spostano con l'immagine
POINT_Y = ("y", "y1", "y2")
SIZES = ("w", "h")                   # misure che crescono e calano con l'immagine
# restano come sono: spessori, dimensione dei testi, posizione e misura del riquadro ingrandito dello zoom

TWO_ENDS = ("arrow", "link")          # due estremi, ognuno legato alla sua immagine
# estremo -> (coordinate x, coordinate y, misure) che si spostano con la sua immagine
END_KEYS = {1: (("x1",), ("y1",), ("w1", "h1")), 2: (("x2",), ("y2",), ("w2", "h2"))}


class Board:
    """Layout, riquadri e annotazioni. Le immagini vere stanno in `images` (id -> PIL), i riquadri le citano per id."""

    def __init__(self) -> None:
        self.layout: str | None = None
        self.format = "16:9"
        self.gap = 12                   # spazio fra i riquadri e ai bordi, in pixel del foglio
        self.bg = "#0B1220"             # colore del foglio fra i riquadri e attorno alle immagini
        self.caption = ""               # testo della didascalia per Word, dopo "Figura N :" e prima delle note
        self.cells: list[dict] = []
        self.images: dict[str, Image.Image] = {}
        self.sources: dict[str, str] = {}   # id dell'immagine -> file da cui viene (se c'e')
        self.project = Project()        # solo per gli effetti (annotazioni) e la misura del foglio
        self.project.fps = 25.0
        self._apply_format()

    # ------------------------------------------------------------- forma

    @property
    def size(self) -> tuple[int, int]:
        return self.project.width, self.project.height

    def _apply_format(self) -> None:
        _name, w, h = FORMATS[self.format]
        self.project.width, self.project.height = w, h

    def set_format(self, key: str) -> None:
        if key in FORMATS:
            old_w, old_h = self.size
            before = self.views()
            self.format = key
            self._apply_format()
            new_w, new_h = self.size
            if (old_w, old_h) != (new_w, new_h):
                # quelle del foglio si scalano col foglio, quelle delle immagini seguono la loro vista
                kx, ky = new_w / old_w, new_h / old_h
                for fx in self.project.effects:
                    if fx.get("type") in TWO_ENDS:
                        for end, (xs, ys, sizes) in END_KEYS.items():
                            if not fx.get(f"cell{end}"):
                                _scale_keys(fx, xs, ys, sizes, kx, ky)
                    elif not fx.get("cell"):
                        _scale_effects([fx], kx, ky)
                self.follow_views(before)

    def set_gap(self, gap: int) -> None:
        before = self.views()
        self.gap = max(0, int(gap))
        self.follow_views(before)

    def set_layout(self, key: str) -> None:
        """Nuovo layout: le immagini gia' messe restano, nell'ordine, nei primi riquadri."""
        count = LAYOUTS[key][0]
        before = self.views()
        self.layout = key
        filled = [c for c in self.cells if c.get("image")]
        empty = [c for c in self.cells if not c.get("image")]
        cells = (filled + empty)[:count]
        while len(cells) < count:
            cells.append(new_cell())
        self.cells = cells
        self.follow_views(before)

    def rects(self) -> list[tuple[int, int, int, int]]:
        """Riquadri in pixel del foglio (x, y, larghezza, altezza), con lo spazio `gap` fra l'uno e l'altro."""
        if self.layout is None:
            return []
        W, H = self.size
        g = self.gap
        out = []
        for fx, fy, fw, fh in LAYOUTS[self.layout][2]:
            x0 = g + fx * (W - g)
            y0 = g + fy * (H - g)
            x1 = g + (fx + fw) * (W - g) - g
            y1 = g + (fy + fh) * (H - g) - g
            out.append((int(round(x0)), int(round(y0)), max(1, int(round(x1 - x0))), max(1, int(round(y1 - y0)))))
        return out

    def cell_at(self, x: float, y: float) -> int | None:
        for i, (cx, cy, cw, ch) in enumerate(self.rects()):
            if cx <= x < cx + cw and cy <= y < cy + ch:
                return i
        return None

    # ------------------------------------------------------------- immagini

    def add_image(self, image: Image.Image, source: str | None = None) -> str:
        image = ImageOps.exif_transpose(image)
        image = image.convert("RGBA") if image.mode in ("RGBA", "LA", "P") else image.convert("RGB")
        key = uuid.uuid4().hex[:10]
        self.images[key] = image
        if source:
            self.sources[key] = os.path.abspath(source)
        return key

    def put(self, index: int, image: Image.Image, name: str = "", source: str | None = None) -> None:
        cell = self.cells[index]
        cell.update(new_cell(), id=cell["id"], image=self.add_image(image, source), name=name)

    def clear_cell(self, index: int) -> None:
        """Toglie l'immagine; le sue annotazioni passano al foglio (restano dove sono)."""
        cell = self.cells[index]
        for fx in self.project.effects:
            for key in ("cell", "cell1", "cell2"):
                if fx.get(key) == cell["id"]:
                    fx.pop(key)
        cell.update(new_cell(), id=cell["id"])

    def image_of(self, index: int) -> Image.Image | None:
        key = self.cells[index].get("image")
        return self.images.get(key) if key else None

    def base_scale(self, index: int) -> float:
        """Scala che fa stare l'immagine intera nel riquadro (zoom 1)."""
        image = self.image_of(index)
        if image is None:
            return 1.0
        _x, _y, w, h = self.rects()[index]
        return min(w / image.width, h / image.height)

    def cover_zoom(self, index: int) -> float:
        """Zoom che riempie tutto il riquadro (l'immagine sborda sul lato lungo)."""
        image = self.image_of(index)
        if image is None:
            return 1.0
        _x, _y, w, h = self.rects()[index]
        return max(w / image.width, h / image.height) / min(w / image.width, h / image.height)

    def zoom_at(self, index: int, factor: float, px: float, py: float) -> None:
        """Ingrandisce l'immagine del riquadro tenendo fermo il punto (px, py) del foglio sotto il mouse."""
        image = self.image_of(index)
        if image is None:
            return
        cell = self.cells[index]
        before = self.views()
        x, y, w, h = self.rects()[index]
        s = self.base_scale(index) * cell["zoom"]
        # punto dell'immagine sotto il mouse, prima
        ix = cell["cx"] * image.width + (px - (x + w / 2)) / s
        iy = cell["cy"] * image.height + (py - (y + h / 2)) / s
        cell["zoom"] = min(MAX_ZOOM, max(MIN_ZOOM, cell["zoom"] * factor))
        s = self.base_scale(index) * cell["zoom"]
        cell["cx"] = (ix - (px - (x + w / 2)) / s) / image.width
        cell["cy"] = (iy - (py - (y + h / 2)) / s) / image.height
        self.clamp(index)
        self.follow_views(before)

    def pan(self, index: int, dx: float, dy: float) -> None:
        """Sposta l'immagine nel riquadro di (dx, dy) pixel del foglio."""
        image = self.image_of(index)
        if image is None:
            return
        before = self.views()
        cell = self.cells[index]
        s = self.base_scale(index) * cell["zoom"]
        cell["cx"] -= dx / s / image.width
        cell["cy"] -= dy / s / image.height
        self.clamp(index)
        self.follow_views(before)

    def set_view(self, index: int, zoom: float | None = None, cx: float | None = None, cy: float | None = None) -> None:
        """Ingrandimento e centro del riquadro scelti dal pannello (Adatta, Riempi, cursore)."""
        before = self.views()
        cell = self.cells[index]
        if zoom is not None:
            cell["zoom"] = min(MAX_ZOOM, max(MIN_ZOOM, float(zoom)))
        if cx is not None:
            cell["cx"] = cx
        if cy is not None:
            cell["cy"] = cy
        self.clamp(index)
        self.follow_views(before)

    def clamp(self, index: int) -> None:
        cell = self.cells[index]
        cell["cx"] = min(1.0, max(0.0, cell["cx"]))
        cell["cy"] = min(1.0, max(0.0, cell["cy"]))

    # ------------------------------------------------------------- annotazioni legate alle immagini

    def transform(self, index: int) -> tuple[float, float, float] | None:
        """(sinistra, alto, scala): il punto (u, v) dell'immagine sta sul foglio in (sinistra + u*s, alto + v*s)."""
        image = self.image_of(index)
        if image is None or self.layout is None:
            return None
        cell = self.cells[index]
        x, y, w, h = self.rects()[index]
        s = self.base_scale(index) * cell["zoom"]
        return x + w / 2 - cell["cx"] * image.width * s, y + h / 2 - cell["cy"] * image.height * s, s

    def views(self) -> dict[str, tuple[float, float, float]]:
        """La vista di ogni riquadro con un'immagine, da confrontare dopo un cambiamento."""
        out = {}
        for index, cell in enumerate(self.cells):
            view = self.transform(index)
            if view is not None:
                out[cell["id"]] = view
        return out

    def follow_views(self, before: dict) -> None:
        """Le annotazioni dei riquadri la cui vista e' cambiata tornano sullo stesso punto della loro immagine."""
        after = self.views()

        def changed(cid):
            old, new = before.get(cid), after.get(cid)
            return None if old is None or new is None or old == new else (old, new)

        for fx in self.project.effects:
            if fx.get("type") in TWO_ENDS:
                for end, keys in END_KEYS.items():
                    views = changed(fx.get(f"cell{end}"))
                    if views:
                        _follow(fx, *keys, *views)
                continue
            views = changed(fx.get("cell"))
            if not views:
                continue
            if fx.get("type") == "zoom" and not fx.get("iw"):
                fx["iw"], fx["ih"] = fx["w"], fx["h"]      # il riquadro ingrandito resta della sua misura
            k = _follow(fx, POINT_X, POINT_Y, SIZES, *views)
            if fx.get("type") == "pixelate" and "block" in fx:
                fx["block"] = max(2, int(round(fx["block"] * k)))

    def anchor(self, fx: dict) -> None:
        """L'annotazione appartiene al riquadro con immagine in cui sta tutta (o al foglio, se ne esce)."""
        for key in ("cell", "cell1", "cell2"):
            fx.pop(key, None)
        if fx.get("type") == "logo":
            return
        if fx.get("type") in TWO_ENDS:                           # ogni estremo segue la sua immagine
            for end in (1, 2):
                px = fx[f"x{end}"] + fx.get(f"w{end}", 0) / 2
                py = fx[f"y{end}"] + fx.get(f"h{end}", 0) / 2
                index = self.cell_at(px, py)
                if index is not None and self.image_of(index) is not None:
                    fx[f"cell{end}"] = self.cells[index]["id"]
            return
        if fx.get("type") == "zoom":                             # l'area ingrandita, non il riquadro
            x0, y0, x1, y1 = fx["x"], fx["y"], fx["x"] + fx["w"], fx["y"] + fx["h"]
        else:
            x0, y0, x1, y1 = overlays.effect_bbox(fx)
        index = self.cell_at((x0 + x1) / 2, (y0 + y1) / 2)
        if index is None or self.image_of(index) is None:
            return
        cx, cy, cw, ch = self.rects()[index]
        if cx <= x0 and cy <= y0 and x1 <= cx + cw and y1 <= cy + ch:
            fx["cell"] = self.cells[index]["id"]
        # a cavallo di due immagini (o dello spazio fra loro): del foglio, si vede intera

    # ------------------------------------------------------------- composizione

    def compose(self, scale: float = 1.0, fast: bool = False) -> Image.Image:
        """Il foglio con le immagini nei riquadri, senza annotazioni, alla scala data."""
        W, H = self.size
        out_w, out_h = max(2, int(round(W * scale))), max(2, int(round(H * scale)))
        sheet = Image.new("RGB", (out_w, out_h), self.bg)
        resample = Image.BILINEAR if fast else Image.LANCZOS
        for index, (x, y, w, h) in enumerate(self.rects()):
            image = self.image_of(index)
            if image is None:
                continue
            cell = self.cells[index]
            s = self.base_scale(index) * cell["zoom"]            # pixel del foglio per pixel dell'immagine
            left = x + w / 2 - cell["cx"] * image.width * s
            top = y + h / 2 - cell["cy"] * image.height * s
            # parte visibile: intersezione fra immagine scalata e riquadro, in pixel del foglio
            vx0, vy0 = max(x, left), max(y, top)
            vx1, vy1 = min(x + w, left + image.width * s), min(y + h, top + image.height * s)
            if vx1 - vx0 < 1 or vy1 - vy0 < 1:
                continue
            box = ((vx0 - left) / s, (vy0 - top) / s, (vx1 - left) / s, (vy1 - top) / s)
            tx0, ty0 = int(round(vx0 * scale)), int(round(vy0 * scale))
            tx1, ty1 = int(round(vx1 * scale)), int(round(vy1 * scale))
            if tx1 - tx0 < 1 or ty1 - ty0 < 1:
                continue
            part = image.resize((tx1 - tx0, ty1 - ty0), resample, box=box)
            if part.mode == "RGBA":
                sheet.paste(part, (tx0, ty0), part)
            else:
                sheet.paste(part, (tx0, ty0))
        return sheet

    def render(self, scale: float = 1.0, fast: bool = False) -> Image.Image:
        """Il foglio finito: immagini e annotazioni (quelle di un'immagine restano dentro il suo riquadro)."""
        sheet = self.compose(scale, fast)
        effects = [fx for fx in self.project.effects if not fx.get("hidden")]
        rects = {cell["id"]: rect for cell, rect in zip(self.cells, self.rects())}
        for cid, (x, y, w, h) in rects.items():
            own = [fx for fx in effects if fx.get("cell") == cid and fx.get("type") != "zoom"]
            if not own:
                continue
            layer = overlays.compose(_Effects(self.project, own), 0.5, sheet, None, scale=scale)
            box = (int(round(x * scale)), int(round(y * scale)), int(round((x + w) * scale)), int(round((y + h) * scale)))
            sheet.paste(layer.crop(box), box[:2])
        # foglio, zoom (il riquadro ingrandito puo' stare ovunque), frecce e collegamenti: non si ritagliano
        rest = [fx for fx in effects if fx.get("cell") not in rects or fx.get("type") == "zoom"]
        return overlays.compose(_Effects(self.project, rest), 0.5, sheet, None, scale=scale)

    # ------------------------------------------------------------- file del progetto

    def save(self, path: str) -> None:
        """Scrive il progetto in `path` (JSON) e i suoi file nella cartella "<nome>_file" accanto."""
        path = os.path.abspath(path)
        base = os.path.dirname(path)
        folder_name = os.path.splitext(os.path.basename(path))[0] + "_file"
        folder = os.path.join(base, folder_name)
        os.makedirs(folder, exist_ok=True)

        def keep(source: str, name: str) -> str:
            """Copia `source` nella cartella come `name` + la sua estensione; restituisce il percorso relativo."""
            target = os.path.join(folder, name + os.path.splitext(source)[1].lower())
            if not (os.path.exists(target) and os.path.samefile(source, target)):
                shutil.copyfile(source, target)
            return folder_name + "/" + os.path.basename(target)

        cells = []
        for cell in self.cells:
            out = {k: cell[k] for k in ("id", "name", "zoom", "cx", "cy")}
            key = cell.get("image")
            out["image"] = None
            if key and key in self.images:
                source = self.sources.get(key)
                if source and os.path.isfile(source):
                    out["image"] = keep(source, f"immagine_{cell['id']}")
                else:
                    target = os.path.join(folder, f"immagine_{cell['id']}.png")
                    self.images[key].save(target, "PNG")
                    out["image"] = folder_name + "/" + os.path.basename(target)
                self.sources[key] = os.path.join(base, out["image"])
            cells.append(out)
        effects = copy.deepcopy(self.project.effects)
        for fx in effects:
            for field, prefix in (("image", "sopra"), ("logo", "logo")):
                if fx.get(field) and os.path.isfile(str(fx[field])):
                    fx[field] = keep(str(fx[field]), f"{prefix}_{fx['id']}")
        data = {"kind": PROJECT_KIND, "version": PROJECT_VERSION, "format": self.format, "layout": self.layout,
                "gap": self.gap, "bg": self.bg, "caption": self.caption, "cells": cells, "annotations": effects}
        write_atomic(path, json.dumps(data, ensure_ascii=False, indent=2))

    @classmethod
    def load(cls, path: str) -> "Board":
        """Il progetto salvato in `path`. ValueError se non e' un progetto di immagini di EditSimple."""
        path = os.path.abspath(path)
        base = os.path.dirname(path)
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict) or data.get("kind") != PROJECT_KIND:
            raise ValueError("not an EditSimple images project")
        board = cls()
        if data.get("format") in FORMATS:
            board.format = data["format"]
            board._apply_format()
        board.layout = data.get("layout") if data.get("layout") in LAYOUTS else None
        board.gap = max(0, int(data.get("gap", board.gap)))
        board.bg = str(data.get("bg") or board.bg)
        board.caption = str(data.get("caption") or "")
        for item in data.get("cells") or []:
            cell = new_cell()
            cell.update({k: item[k] for k in ("id", "name", "zoom", "cx", "cy") if k in item})
            if item.get("image"):
                source = os.path.join(base, item["image"])
                with Image.open(source) as image:
                    image.load()
                    cell["image"] = board.add_image(image, source)
            board.cells.append(cell)
        if board.layout is not None:
            count = LAYOUTS[board.layout][0]
            board.cells = (board.cells + [new_cell() for _ in range(count)])[:count]
        for fx in data.get("annotations") or []:
            for field in ("image", "logo"):
                value = fx.get(field)
                if value and not os.path.isabs(str(value)):
                    fx[field] = os.path.join(base, str(value))
            board.project.add_effect(fx)
        board.project.dirty = False
        return board

    # ------------------------------------------------------------- annulla

    def snapshot(self) -> dict:
        return {"layout": self.layout, "format": self.format, "gap": self.gap, "bg": self.bg, "caption": self.caption,
                "cells": copy.deepcopy(self.cells), "effects": copy.deepcopy(self.project.effects)}

    def restore(self, state: dict) -> None:
        self.layout = state["layout"]
        self.format = state["format"]
        self.gap = state["gap"]
        self.bg = state["bg"]
        self.caption = state.get("caption", "")
        self.cells = copy.deepcopy(state["cells"])
        self.project.effects = copy.deepcopy(state["effects"])
        self._apply_format()


class _Effects:
    """Un Project ridotto a un gruppo di effetti, per comporli con overlays.compose."""

    def __init__(self, project: Project, effects: list[dict]) -> None:
        self.width, self.height = project.width, project.height
        self.clock = project.clock
        self._effects = effects

    def effects_at(self, t: float, types=None) -> list[dict]:
        return [fx for fx in self._effects if types is None or fx["type"] in types]


def _follow(fx: dict, xs, ys, sizes, old: tuple, new: tuple) -> float:
    """Riporta le chiavi date sullo stesso punto dell'immagine dopo che la sua vista e' passata da old a new."""
    (lo, to, so), (ln, tn, sn) = old, new
    k = sn / so
    for key in xs:
        if key in fx:
            fx[key] = ln + (fx[key] - lo) * k
    for key in ys:
        if key in fx:
            fx[key] = tn + (fx[key] - to) * k
    for key in sizes:
        if key in fx:
            fx[key] = max(2.0, fx[key] * k)
    return k


def _scale_keys(fx: dict, xs, ys, sizes, kx: float, ky: float) -> None:
    for key in xs:
        if key in fx:
            fx[key] = fx[key] * kx
    for key in ys:
        if key in fx:
            fx[key] = fx[key] * ky
    for key in sizes:
        if key in fx:
            fx[key] = max(1, fx[key] * min(kx, ky))


def _scale_effects(effects: list[dict], kx: float, ky: float) -> None:
    """Cambio di formato: le annotazioni restano nello stesso punto relativo del foglio."""
    k = min(kx, ky)
    for fx in effects:
        for key in ("x", "x1", "x2", "bx"):
            if key in fx:
                fx[key] = fx[key] * kx
        for key in ("y", "y1", "y2", "by"):
            if key in fx:
                fx[key] = fx[key] * ky
        for key in ("w", "h", "iw", "ih", "w1", "h1", "w2", "h2", "size", "thickness"):
            if key in fx:
                fx[key] = max(1, fx[key] * k)
