# EditSimple — montaggio video per presentazioni.  Copyright (C) 2026 Andrea Cumini <andrea@osintinfo.net>
# SPDX-License-Identifier: GPL-3.0-only
# GNU GPL v3 con termini aggiuntivi (attribuzione dell'autore): vedi LICENSE e NOTICE.
"""Pagina Immagini: annotare immagini ferme, da sole o affiancate per un confronto.

Si sceglie un layout (da 1 a 4 immagini) e il formato del foglio; ogni
riquadro si riempie con un clic (file o appunti), trascinandoci un file o con
Ctrl+V. Con la rotellina l'immagine si ingrandisce nel suo riquadro,
trascinandola si sposta. Le annotazioni sono quelle del video (testo,
immagine, logo, riquadro, ovale, freccia, zoom, pixelatura), ferme: niente
tempi ne' inseguimento. Il risultato si esporta in PNG o JPG o si copia negli
appunti.

Per testi, logo e caratteri la pagina usa le stesse funzioni della finestra
principale (App), che lavorano su `self.project`: qui e' il Project della tavola.
"""

from __future__ import annotations

import json
import os
import threading
import time
import tkinter as tk
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image

from . import imageboard, overlays, theme, widgets, winshell, wordcopy
from .fonts import default_font
from .i18n import N_, tr
from .imageboard import FORMATS, LAYOUTS, Board
from .panels import PropertiesPanel
from .preview_view import PreviewView
from .widgets import messagebox

IMAGE_TYPES = "*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tif *.tiff"
WHEEL_STEP = 1.15          # ingrandimento a ogni scatto della rotellina
# strumenti: chiave del glifo, nome, modo di disegno (o azione), suggerimento
TOOLS = (
    ("text", N_("Testo"), "text", N_("Testo (T): clic dove metterlo")),
    ("image", N_("Immagine"), "@image", N_("Immagine sopra il foglio, da spostare e ridimensionare")),
    ("logo", N_("Logo"), "@logo", N_("Logo e testo dell'operatore della Configurazione (L)")),
    ("box", N_("Riquadro"), "box", N_("Riquadro (R)")),
    ("oval", N_("Ovale"), "oval", N_("Ovale (E)")),
    ("arrow", N_("Freccia"), "arrow", N_("Freccia (A): dalla coda alla punta")),
    ("link", N_("Collega"), "link", N_("Collega due punti con riquadri e una linea (C)")),
    ("linko", "", "link_oval", N_("Collega due punti con ovali e una linea (Maiusc+C)")),
    ("num", N_("Numeri"), "marker_number", N_("Punto numerato 1, 2, 3 (N): clic dove metterlo, il prossimo prende il numero dopo")),
    ("abc", N_("Lettere"), "marker_letter", N_("Punto con lettera A, B, C (Maiusc+N): clic dove metterlo, il prossimo prende la lettera dopo")),
    ("zoom", N_("Zoom"), "zoom", N_("Zoom rettangolare (Z): l'area scelta in un riquadro ingrandito")),
    ("zoomo", "", "zoom_oval", N_("Zoom ovale (Maiusc+Z)")),
    ("pixel", N_("Pixel"), "pixelate", N_("Pixelatura rettangolare (P)")),
    ("pixelo", "", "pixelate_oval", N_("Pixelatura ovale (K)")),
)
KEYS = {"t": "text", "r": "box", "e": "oval", "a": "arrow", "z": "zoom", "Z": "zoom_oval", "p": "pixelate",
        "k": "pixelate_oval", "c": "link", "C": "link_oval", "n": "marker_number", "N": "marker_letter"}


def _app_method(name: str):
    """Una funzione della finestra principale, da chiamare con la pagina al posto di App (import tardivo)."""
    from .app import App
    return getattr(App, name)


class ImagePage(ctk.CTkFrame):
    def __init__(self, master, app) -> None:
        super().__init__(master, fg_color=theme.BG, corner_radius=0)
        self.app = app
        self.fonts = app.fonts
        self.config_store = app.config_store
        self.board = Board()
        self.playhead = 0.5                 # le annotazioni durano da 0 a 1: l'istante e' sempre dentro
        self.undo_stack: list[dict] = []
        self.redo_stack: list[dict] = []
        self.selected_kind: str | None = None
        self.selected_id = None
        self.active_cell: int | None = None
        self._render_job: str | None = None
        self._cell_drag: dict | None = None
        self._last_wheel = 0.0
        self._pixel_shape = "rect"
        self._marker_style = "number"      # punti numerati: "number" o "letter"
        self._zoom_shape = "rect"
        self._hover: int | None = None      # riquadro sotto il mouse: Ctrl+V incolla li'
        self.path: str | None = None        # file JSON del progetto, se salvato
        self._word_busy = False             # inserimento in Word in corso
        self._saved_state = self._state()
        self._build()
        self.after(100, self.refresh)

    # ------------------------------------------------------------- per i pannelli e le funzioni di App

    @property
    def project(self):
        return self.board.project

    def status(self, text: str) -> None:
        self.app.status(text)

    def push_undo(self) -> None:
        self.undo_stack.append(self.board.snapshot())
        if len(self.undo_stack) > 60:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def undo(self) -> None:
        if self.undo_stack:
            self.redo_stack.append(self.board.snapshot())
            self.board.restore(self.undo_stack.pop())
            self.select(None, None)
            self.refresh()

    def redo(self) -> None:
        if self.redo_stack:
            self.undo_stack.append(self.board.snapshot())
            self.board.restore(self.redo_stack.pop())
            self.select(None, None)
            self.refresh()

    # testi, logo, caratteri, centratura: le stesse funzioni della finestra principale
    def edit_text(self, fx: dict) -> None:
        _app_method("edit_text")(self, fx)

    def _center_fx(self, fx: dict, axis: str) -> None:
        _app_method("_center_fx")(self, fx, axis)

    def center_effect(self, fx: dict, axis: str) -> None:
        _app_method("center_effect")(self, fx, axis)

    def place_logo(self, fx: dict) -> None:
        _app_method("place_logo")(self, fx)

    def _remember_text_style(self, values: dict) -> None:
        _app_method("_remember_text_style")(self, values)

    def _text_values(self) -> dict:
        return _app_method("_text_values")(self)

    def ask_image_file(self, current: str = "") -> str:
        return _app_method("ask_image_file")(self, current)

    def ask_logo_file(self, current: str = "") -> str:
        return _app_method("ask_logo_file")(self, current)

    def pick_font(self, current: str, sample: str, callback) -> None:
        _app_method("pick_font")(self, current, sample, callback)

    def delete_effect(self, effect_id: str) -> None:
        self.push_undo()
        self.project.remove_effect(effect_id)
        self.select(None, None)
        self.refresh()

    # ------------------------------------------------------------- costruzione

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        bar = ctk.CTkFrame(self, fg_color=theme.PANEL, corner_radius=4, border_width=1, border_color=theme.BORDER)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=theme.PAD, pady=(theme.PAD, theme.GAP))
        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=10, pady=(6, 8))
        self.tool_buttons: dict[str, ctk.CTkButton] = {}
        g = self.app._group(inner, tr("Progetto"))
        self._tool(g, "open", N_("Apri"), self.open_project, N_("Apri un progetto di immagini salvato (Ctrl+O)"))
        self._tool(g, "save", N_("Salva"), self.save_project,
                   N_("Salva il progetto: un file JSON e una cartella con le immagini, modificabili (Ctrl+S; "
                      "Ctrl+Maiusc+S: salva con nome)"))
        g = self.app._group(inner, tr("Immagini"))
        self._tool(g, "fit", N_("Layout"), self.show_layouts, N_("Scegli quante immagini e come disporle"))
        self._tool(g, "folder", N_("Carica"), lambda: self.load_files(self._target_cell()),
                   N_("Carica una o piu' immagini nel riquadro scelto e nei successivi vuoti"))
        self._tool(g, "undo", "", self.undo, N_("Annulla (Ctrl+Z)"))
        self._tool(g, "redo", "", self.redo, N_("Ripeti (Ctrl+Y)"))
        g = self.app._group(inner, tr("Annotazioni"))
        for glyph, label, mode, tip in TOOLS:
            command = (lambda m=mode: self.start_draw(m)) if not mode.startswith("@") else \
                {"@image": self.add_image, "@logo": self.add_logo}[mode]
            self._tool(g, glyph, label, command, tip)
        g = self.app._group(inner, tr("Uscita"))
        self._tool(g, "edit", N_("Didascalia"), self.edit_caption,
                   N_("Scrive o cambia il testo della didascalia per Word (quello dopo \"Figura N :\")"))
        self._tool(g, "export", N_("Esporta"), self.export, N_("Salva il foglio in PNG o JPG"), primary=True)
        self._tool(g, "save", N_("Copia"), self.copy_to_clipboard, N_("Copia il foglio negli appunti, da incollare altrove"))
        self._tool(g, "word", N_("Word"), self.copy_for_word,
                   N_("Inserisce l'immagine con la didascalia (i punti numerati e le loro note) nel documento Word "
                      "aperto, dove c'e' il cursore"))

        self.preview = PreviewView(self, on_draw=self._on_draw, on_select=self._on_preview_select,
                                   on_edit_start=lambda fx: self.push_undo(), on_edit=self._on_preview_edit,
                                   on_wheel=lambda _d: None, active_effects=lambda: self.project.effects_at(self.playhead))
        self.preview.time = self.playhead
        self.preview.placeholder = N_("Scegli un layout per cominciare")
        self.preview.grid(row=1, column=0, sticky="nsew", padx=(theme.PAD, theme.GAP))
        self.preview.on_resize = self.schedule_render
        self.preview.on_edit_text = self.edit_text
        self.preview.on_redraw = self._draw_cells
        self.preview.on_wheel_at = self._wheel
        self.preview.on_empty_press = self._cell_press
        self.preview.on_empty_drag = self._cell_drag_move
        self.preview.on_empty_release = self._cell_release
        self.preview.canvas.bind("<Motion>", self._hover_cell, add="+")
        self.preview.canvas.bind("<Leave>", lambda _e: setattr(self, "_hover", None), add="+")
        winshell.accept_files(self.preview.canvas, self._dropped)

        self.panel = PropertiesPanel(self, self.fonts, self, static=True)
        self.panel.extra_builders["empty"] = (lambda: tr("Foglio"), self._build_sheet_panel)
        self.panel.extra_builders["cell"] = (lambda: tr("Riquadro {n}").format(n=(self.active_cell or 0) + 1),
                                             self._build_cell_panel)
        self.panel.grid(row=1, column=1, sticky="nsew", padx=(0, theme.PAD))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid(row=2, column=0, columnspan=2, sticky="ew", padx=theme.PAD, pady=(theme.GAP, theme.PAD))
        self.mode_label = ctk.CTkLabel(row, text="", font=self.fonts.bold, text_color=theme.ACCENT, anchor="w")
        self.mode_label.pack(side="left")

        self.chooser = self._build_chooser()
        self.select(None, None)             # il pannello mostra il foglio, non le istruzioni del video

    def _tool(self, parent, glyph: str, text: str, command, tooltip: str = "", primary: bool = False) -> ctk.CTkButton:
        app = self.app

        def compose() -> str:
            words = tr(text) if text else ""
            if app._has_icons:
                return app._glyph(glyph) + ("  " + words if words else "")
            return words or app._glyph(glyph)

        item = widgets.button(parent, compose(), command, primary=primary, height=30, width=10,
                              font=ctk.CTkFont(family=theme.icon_font() or theme.ui_font(), size=12, weight="bold")
                              if app._has_icons else self.fonts.button)
        item.retranslate = lambda: item.configure(text=compose())
        item.pack(side="left", padx=(0, 4))
        self.tool_buttons[text or glyph] = item     # per chi deve ritrovarlo (screenshot del manuale)
        if tooltip:
            widgets.Tooltip(item, tr(tooltip), self.fonts)
        return item

    # ------------------------------------------------------------- scelta del layout

    def _build_chooser(self) -> ctk.CTkFrame:
        box = ctk.CTkFrame(self, fg_color=theme.PANEL, corner_radius=6, border_width=1, border_color=theme.BORDER)
        title = ctk.CTkLabel(box, text=tr("Scegli il layout"), font=self.fonts.page, text_color=theme.TEXT)
        title.pack(anchor="w", padx=18, pady=(14, 2))
        widgets.note(box, tr("Quante immagini e come disporle: si puo' cambiare in ogni momento, le immagini gia' "
                             "messe restano."), self.fonts).pack(anchor="w", padx=18)
        for count in (1, 2, 3, 4):
            row = ctk.CTkFrame(box, fg_color="transparent")
            row.pack(anchor="w", padx=18, pady=(10, 0))
            caption = ctk.CTkLabel(row, text=str(count), font=self.fonts.page, text_color=theme.ACCENT, width=28)
            caption.pack(side="left", padx=(0, 8))
            for key, (n, name, rects) in LAYOUTS.items():
                if n == count:
                    self._layout_button(row, key, name, rects)
        frow = ctk.CTkFrame(box, fg_color="transparent")
        frow.pack(anchor="w", padx=18, pady=(14, 0))
        ctk.CTkLabel(frow, text=tr("Formato del foglio"), font=self.fonts.small, text_color=theme.TEXT_SOFT).pack(side="left", padx=(0, 8))
        names = {key: tr(name) for key, (name, _w, _h) in FORMATS.items()}
        inverse = {v: k for k, v in names.items()}
        self._format_var = tk.StringVar(value=names[self.board.format])
        ctk.CTkOptionMenu(frow, variable=self._format_var, values=list(names.values()), width=180,
                          command=lambda v: self._set_format(inverse.get(v, "16:9"))).pack(side="left")
        close = widgets.button(box, tr("Chiudi"), self.hide_layouts, width=90)
        close.pack(anchor="e", padx=18, pady=(14, 14))
        self._chooser_close = close
        return box

    def _layout_button(self, parent, key: str, name: str, rects) -> None:
        cell = ctk.CTkFrame(parent, fg_color="transparent")
        cell.pack(side="left", padx=(0, 10))
        canvas = tk.Canvas(cell, width=112, height=66, bg=theme.BG, highlightthickness=1,
                           highlightbackground=theme.BORDER, cursor="hand2")
        canvas.pack()
        for fx, fy, fw, fh in rects:
            canvas.create_rectangle(6 + fx * 100 + 2, 5 + fy * 56 + 2, 6 + (fx + fw) * 100 - 2, 5 + (fy + fh) * 56 - 2,
                                    fill=theme.SELECT_BG, outline=theme.ACCENT)
        label = ctk.CTkLabel(cell, text=tr(name), font=self.fonts.tiny, text_color=theme.TEXT_SOFT)
        label.pack()
        for widget in (canvas, label):
            widget.bind("<Button-1>", lambda _e, k=key: self.choose_layout(k))
        canvas.bind("<Enter>", lambda _e: canvas.configure(highlightbackground=theme.ACCENT))
        canvas.bind("<Leave>", lambda _e: canvas.configure(highlightbackground=theme.BORDER))

    def show_layouts(self) -> None:
        self.cancel_mode()
        self._chooser_close.configure(state="normal" if self.board.layout else "disabled")
        self.chooser.place(relx=0.5, rely=0.5, anchor="center")
        self.chooser.lift()

    def hide_layouts(self) -> None:
        if self.board.layout:
            self.chooser.place_forget()

    def choose_layout(self, key: str) -> None:
        self.push_undo()
        self.board.set_layout(key)
        self.active_cell = 0
        self.chooser.place_forget()
        self.select(None, None)
        self.refresh()
        self.status(tr("Layout: {name}. Clicca un riquadro, trascinaci un file o usa Ctrl+V.").format(
            name=tr(LAYOUTS[key][1])))

    def _set_format(self, key: str) -> None:
        if key != self.board.format:
            self.push_undo()
            self.board.set_format(key)
            self._format_var.set(tr(FORMATS[key][0]))       # la scelta del layout mostra il formato attuale
            if self.selected_kind is None:
                self.select(None, None)                     # e anche il pannello del foglio
            self.refresh()

    # ------------------------------------------------------------- disegno

    def schedule_render(self) -> None:
        if self._render_job is None:
            self._render_job = self.after(10, self._render)

    def _render(self) -> None:
        self._render_job = None
        if self.board.layout is None:
            self.preview.set_frame(None)
            return
        self.preview.set_project_size(self.board.size)
        dw, _dh = self.preview.display_size()
        scale = dw / self.board.size[0]
        self.preview.set_frame(self.board.render(scale, fast=True))

    def refresh(self) -> None:
        self.schedule_render()
        if self.selected_kind == "effect" and self.project.effect_by_id(self.selected_id) is None:
            self.select(None, None)
        else:
            self.panel.refresh()
        if self.board.layout is None and self.app._page == "image":
            self.show_layouts()

    def _draw_cells(self) -> None:
        """Bordi dei riquadri, riquadro attivo e invito a caricare nei riquadri vuoti (non finiscono nell'immagine)."""
        c = self.preview.canvas
        for index, (x, y, w, h) in enumerate(self.board.rects()):
            x0, y0 = self.preview._to_canvas(x, y)
            x1, y1 = self.preview._to_canvas(x + w, y + h)
            empty = self.board.image_of(index) is None
            active = index == self.active_cell
            if empty:
                c.create_rectangle(x0 + 2, y0 + 2, x1 - 2, y1 - 2, outline=theme.ACCENT if active else theme.TEXT_FAINT,
                                   width=2, dash=(6, 4))
                c.create_text((x0 + x1) / 2, (y0 + y1) / 2,
                              text=tr("Clicca per caricare un'immagine\noppure trascina qui un file\no incolla con Ctrl+V"),
                              fill=theme.TEXT_DIM, font=(theme.ui_font(), 11), justify="center")
            elif active and len(self.board.rects()) > 1:
                c.create_rectangle(x0 + 1, y0 + 1, x1 - 1, y1 - 1, outline=theme.ACCENT, width=2)

    # ------------------------------------------------------------- riquadri: mouse

    def _project_point(self, event) -> tuple[float, float]:
        p = self.preview
        return (event.x - p._ox) / p._scale, (event.y - p._oy) / p._scale

    def _hover_cell(self, event) -> None:
        if self.board.layout is None or self.preview.mode:
            return
        if self._cell_drag is None:
            self._hover = self.board.cell_at(*self._project_point(event))

    def _target_cell(self) -> int:
        """Il riquadro su cui caricare: quello attivo, se no il primo vuoto, se no il primo."""
        if self.active_cell is not None and self.active_cell < len(self.board.cells):
            return self.active_cell
        for i, cell in enumerate(self.board.cells):
            if not cell.get("image"):
                return i
        return 0

    def _cell_press(self, event) -> bool:
        index = self.board.cell_at(*self._project_point(event))
        if index is None:
            return False
        self.active_cell = index
        self._cell_drag = {"index": index, "x": event.x, "y": event.y, "moved": False}
        self.preview._redraw()
        return True

    def _cell_drag_move(self, event) -> None:
        d = self._cell_drag
        if d is None or self.board.image_of(d["index"]) is None:
            return
        if not d["moved"] and abs(event.x - d["x"]) + abs(event.y - d["y"]) < 3:
            return
        if not d["moved"]:
            d["moved"] = True
            self.push_undo()
            self.preview.canvas.configure(cursor="fleur")
        scale = self.preview._scale
        self.board.pan(d["index"], (event.x - d["x"]) / scale, (event.y - d["y"]) / scale)
        d["x"], d["y"] = event.x, event.y
        self.schedule_render()

    def _cell_release(self, event) -> None:
        d = self._cell_drag
        self._cell_drag = None
        self.preview.canvas.configure(cursor="arrow")
        if d is None or d["moved"]:
            return
        index = d["index"]
        if self.board.image_of(index) is None:
            self._load_menu(index, event)
        else:
            self.select("cell", index)

    def _load_menu(self, index: int, event) -> None:
        menu = tk.Menu(self, tearoff=0, bg=theme.PANEL, fg=theme.TEXT, activebackground=theme.SELECT_BG,
                       activeforeground=theme.TEXT, bd=1, relief="solid")
        menu.add_command(label=tr("Carica da file..."), command=lambda: self.load_files(index))
        menu.add_command(label=tr("Incolla dagli appunti (Ctrl+V)"), command=lambda: self.paste(index))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _wheel(self, event) -> None:
        if self.board.layout is None:
            return
        px, py = self._project_point(event)
        index = self.board.cell_at(px, py)
        if index is None or self.board.image_of(index) is None:
            return
        now = time.time()
        if now - self._last_wheel > 0.8:
            self.push_undo()                      # una rotazione continua della rotellina e' un solo annulla
        self._last_wheel = now
        self.board.zoom_at(index, WHEEL_STEP if event.delta > 0 else 1 / WHEEL_STEP, px, py)
        self.active_cell = index
        self.schedule_render()
        if self.selected_kind == "cell" and self.selected_id == index:
            self.panel.refresh()

    # ------------------------------------------------------------- riquadri: immagini

    def _open_image(self, path: str) -> Image.Image | None:
        try:
            image = Image.open(path)
            image.load()
            return image
        except (OSError, ValueError):
            return None

    def _fill_from(self, index: int, images: list[tuple[Image.Image, str, str | None]]) -> int:
        """Mette le immagini dal riquadro `index` in poi (la prima li', le altre nei riquadri vuoti dopo)."""
        placed = 0
        count = len(self.board.cells)
        after = [(index + k) % count for k in range(1, count)]          # i riquadri dopo, poi quelli prima
        targets = [index] + [i for i in after if not self.board.cells[i].get("image")]
        for (image, name, source), target in zip(images, targets):
            self.board.put(target, image, name, source)
            placed += 1
        return placed

    def load_files(self, index: int | None = None) -> None:
        if self.board.layout is None:
            self.show_layouts()
            return
        index = self._target_cell() if index is None else index
        paths = filedialog.askopenfilenames(title=tr("Carica immagini"), parent=self,
                                            initialdir=self.config_store.get("last_image_dir") or None,
                                            filetypes=[(tr("Immagini"), IMAGE_TYPES), (tr("Tutti i file"), "*.*")])
        if paths:
            self.config_store.set("last_image_dir", os.path.dirname(paths[0]))
            self._load_paths(list(paths), index)

    def _load_paths(self, paths: list[str], index: int) -> None:
        images = []
        bad = []
        for path in paths:
            image = self._open_image(path)
            if image is None:
                bad.append(os.path.basename(path))
            else:
                images.append((image, os.path.basename(path), path))
        if images:
            self.push_undo()
            placed = self._fill_from(index, images)
            self.active_cell = index
            self.select("cell", index)
            self.refresh()
            self.status(tr("{count} immagini caricate.").format(count=placed) if placed > 1 else
                        tr("Immagine caricata: {name}").format(name=images[0][1]))
        if bad:
            messagebox.showwarning(tr("Immagini"), tr("Questi file non si aprono come immagini:\n{files}").format(
                files="\n".join(bad)), self.app)

    def _dropped(self, paths: list[str], x: int, y: int) -> None:
        if self.board.layout is None:
            self.choose_layout("1")
        p = self.preview
        index = self.board.cell_at((x - p._ox) / p._scale, (y - p._oy) / p._scale)
        self._load_paths(paths, self._target_cell() if index is None else index)

    def paste(self, index: int | None = None) -> None:
        if self.board.layout is None:
            self.choose_layout("1")
        image, path = winshell.clipboard_image()
        if image is None:
            self.status(tr("Negli appunti non c'e' un'immagine: copia uno screenshot o un file immagine."))
            return
        if index is None:
            index = self._hover if self._hover is not None else self._target_cell()
        self.push_undo()
        self.board.put(index, image, os.path.basename(path) if path else tr("appunti"), path or None)
        self.active_cell = index
        self.select("cell", index)
        self.refresh()
        self.status(tr("Immagine incollata nel riquadro {n}.").format(n=index + 1))

    def clear_cell(self, index: int) -> None:
        self.push_undo()
        self.board.clear_cell(index)
        self.select(None, None)
        self.refresh()

    def fit_cell(self, index: int, cover: bool = False) -> None:
        self.push_undo()
        self.board.set_view(index, zoom=self.board.cover_zoom(index) if cover else 1.0, cx=0.5, cy=0.5)
        self.panel.refresh()
        self.refresh()

    # ------------------------------------------------------------- selezione e pannello

    def select(self, kind: str | None, item_id, seek: bool = True) -> None:
        self.selected_kind, self.selected_id = kind, item_id
        if kind == "effect":
            fx = self.project.effect_by_id(item_id)
            if fx is None:
                return self.select(None, None)
            self.panel.show("effect", fx)
            self.preview.set_selected(fx)
        elif kind == "cell" and item_id is not None and item_id < len(self.board.cells):
            self.active_cell = item_id
            self.panel.show("cell", self.board.cells[item_id])
            self.preview.set_selected(None)
        else:
            self.selected_kind = self.selected_id = None
            self.panel.show("empty", {"format": self.board.format, "gap": self.board.gap, "bg": self.board.bg})
            self.preview.set_selected(None)

    def _on_preview_select(self, fx: dict | None) -> None:
        self.select("effect" if fx else None, fx["id"] if fx else None)

    def _on_preview_edit(self, fx: dict, final: bool) -> None:
        self.project.dirty = True
        if final:
            self.board.anchor(fx)           # trascinata su un'altra immagine: ora segue quella
            self.refresh()
        else:
            self.panel.refresh()
            self.schedule_render()

    def edit_caption(self) -> None:
        """Il testo della didascalia per Word, in una finestra: si cambia anche quando il pannello
        mostra un'immagine o un'annotazione invece del foglio."""
        text = widgets.ask_note(self.app, tr("Didascalia per Word"), self.board.caption, self.fonts,
                                tr("Va subito dopo \"Figura N :\" nella didascalia che il pulsante Word inserisce; "
                                   "dopo vengono le note dei punti numerati."))
        if text is None or text == self.board.caption:
            return
        self.push_undo()
        self.board.caption = text
        self.project.dirty = True
        if self.selected_kind is None:
            self.select(None, None)         # il pannello del foglio mostra il testo nuovo

    def _build_sheet_panel(self, panel: PropertiesPanel, obj: dict) -> None:
        panel._section(tr("Foglio"))
        names = {key: tr(name) for key, (name, _w, _h) in FORMATS.items()}
        panel._choice("format", tr("Formato"), names, on_apply=lambda k, v: self._set_format(v))
        panel._entry("gap", tr("Spazio fra le immagini (px)"), "int",
                     on_apply=lambda k, v: (self.board.set_gap(v), self.schedule_render()))
        panel._color("bg", tr("Colore del foglio"), on_apply=lambda k, v: self._set_sheet("bg", v))
        panel._button(tr("Cambia layout..."), self.show_layouts)
        panel._section(tr("Didascalia per Word"))
        box = ctk.CTkTextbox(panel.body, height=80, font=self.fonts.body, wrap="word")
        box.pack(fill="x", pady=(2, 0))
        box.insert("1.0", self.board.caption)
        touched = [False]

        def changed(_event) -> None:
            text = box.get("1.0", "end-1c")
            if text == self.board.caption:
                return
            if not touched[0]:
                touched[0] = True
                self.push_undo()
            self.board.caption = text
            self.project.dirty = True

        box.bind("<KeyRelease>", changed)
        widgets.note(panel.body, tr("Va subito dopo \"Figura N :\" nella didascalia che il pulsante Word inserisce; "
                                    "dopo vengono le note dei punti numerati."), self.fonts,
                     wraplength=280).pack(fill="x", pady=(4, 0))
        markers = self.markers()
        if markers:
            panel._section(tr("Punti numerati"))
            for fx in markers:
                note = " ".join(str(fx.get("note") or "").split()) or tr("(nessuna nota)")
                text = f"{fx.get('label', '')}  -  {note if len(note) < 34 else note[:31] + '...'}"
                widgets.button(panel.body, text, lambda f=fx: self.select("effect", f["id"]), height=26,
                               anchor="w").pack(fill="x", pady=(4, 0))
        widgets.note(panel.body, tr("Clicca un riquadro vuoto per caricare un'immagine, oppure trascinaci un file o "
                                    "incollala con Ctrl+V. Rotellina sull'immagine: ingrandisce; trascinandola: si "
                                    "sposta nel suo riquadro. Le annotazioni si aggiungono con gli strumenti in alto, "
                                    "come nel montaggio video. Esporta immagine salva il foglio in PNG o JPG."),
                     self.fonts, wraplength=280).pack(fill="x", pady=(10, 0))

    def _set_sheet(self, key: str, value) -> None:
        setattr(self.board, key, value)
        self.schedule_render()

    def _build_cell_panel(self, panel: PropertiesPanel, cell: dict) -> None:
        index = self.board.cells.index(cell) if cell in self.board.cells else 0
        image = self.board.image_of(index)
        panel._section(tr("Immagine"))
        if image is None:
            panel._label_row(tr("File"), tr("nessuna"))
        else:
            panel._label_row(tr("File"), cell.get("name") or tr("appunti"))
            panel._label_row(tr("Misura"), f"{image.width} x {image.height} px")
            panel._slider("zoom", tr("Ingrandimento"), imageboard.MIN_ZOOM, 8.0,
                          fmt=lambda v: f"{v * 100:.0f} %", on_apply=lambda k, v: self._set_zoom(index, v))
            row = ctk.CTkFrame(panel.body, fg_color="transparent")
            row.pack(fill="x", pady=(8, 0))
            widgets.button(row, tr("Adatta"), lambda: self.fit_cell(index), width=110).pack(side="left", padx=(0, 6))
            widgets.button(row, tr("Riempi"), lambda: self.fit_cell(index, cover=True), width=110).pack(side="left")
        panel._button(tr("Carica da file..."), lambda: self.load_files(index))
        panel._button(tr("Incolla dagli appunti (Ctrl+V)"), lambda: self.paste(index))
        if image is not None:
            panel._button(tr("Togli l'immagine"), lambda: self.clear_cell(index), danger=True)
        widgets.note(panel.body, tr("Rotellina sull'immagine: ingrandisce attorno al mouse. Trascinandola: si sposta "
                                    "nel suo riquadro. Adatta: tutta visibile; Riempi: copre tutto il riquadro."),
                     self.fonts, wraplength=280).pack(fill="x", pady=(8, 0))

    def _set_zoom(self, index: int, value: float) -> None:
        self.board.set_view(index, zoom=value)
        self.schedule_render()

    # ------------------------------------------------------------- annotazioni

    def start_draw(self, mode: str) -> None:
        if self.board.layout is None:
            self.show_layouts()
            return
        self._pixel_shape = "oval" if mode == "pixelate_oval" else "rect"
        if mode == "pixelate_oval":
            mode = "pixelate"
        self._zoom_shape = "oval" if mode == "zoom_oval" else "rect"
        if mode == "zoom_oval":
            mode = "zoom"
        self.preview.zoom_shape = self._zoom_shape
        self.preview.link_shape = "oval" if mode == "link_oval" else "rect"
        if mode == "link_oval":
            mode = "link"
        if mode.startswith("marker_"):
            self._marker_style = mode[7:]
            mode = "marker"
        if mode == "zoom":
            factor = int(self.config_store.get("zoom_factor") or 2)
            self.preview.set_zoom_factor(factor if factor in overlays.ZOOM_FACTORS else 2)
        self.preview.set_mode(mode)
        from .project import EFFECT_NAMES
        self.mode_label.configure(text=tr("Disegna: {effect}  (Esc annulla)").format(effect=tr(EFFECT_NAMES.get(mode, mode))))

    def cancel_mode(self) -> None:
        self.preview.set_mode(None)
        self.mode_label.configure(text="")

    def _new_fx(self, kind: str, **values) -> dict:
        return dict(type=kind, start=0.0, end=1.0, **values)

    def _add(self, fx: dict) -> None:
        self.push_undo()
        self.board.anchor(fx)               # sull'immagine in cui e' disegnata: la seguira'
        self.project.add_effect(fx)
        self.refresh()
        self.select("effect", fx["id"])

    def _on_draw(self, mode: str, geometry: dict) -> None:
        self.cancel_mode()
        W, H = self.board.size
        fx = self._new_fx(mode, **geometry)
        if mode == "text":
            values = widgets.ask_text(self.app, self.fonts, self._text_values(), tr("Nuovo testo"))
            if not values:
                return
            self._remember_text_style(values)
            center = values.pop("center")
            fx.update(values, font=default_font(), bg_color="#000000", bg_alpha=0.55,
                      bg_radius=float(self.config_store.get("round_text")))
            if center:
                self._center_fx(fx, "x")
            self._add(fx)
        elif mode in ("box", "oval"):
            fx.update(color="#FF3B30", thickness=max(3, H // 240), fill=False, fill_alpha=0.25,
                      radius=float(self.config_store.get("round_box")) if mode == "box" else 0.0)
            self._add(fx)
        elif mode == "arrow":
            fx.update(color="#FF3B30", thickness=max(4, H // 180))
            self._add(fx)
        elif mode == "marker":
            fx.update(overlays.new_marker(self.project.effects, self._marker_style, fx["x"], fx["y"], H), note="")
            self._add(fx)
        elif mode == "link":
            fx.update(shape=self.preview.link_shape, color="#FF3B30", thickness=max(3, H // 270), dashed=False,
                      radius=float(self.config_store.get("round_box")))
            self._add(fx)
        elif mode == "zoom":
            cx, cy = fx.pop("cx", None), fx.pop("cy", None)
            factor = int(fx.get("factor") or 2)
            fx.update(factor=factor if factor in overlays.ZOOM_FACTORS else 2, color="#FFD60A",
                      thickness=max(3, H // 270), outline=True, link=True,
                      shape=self._zoom_shape, radius=float(self.config_store.get("round_zoom")))
            overlays.place_inset(fx, cx, cy, W, H)
            self.config_store.set("zoom_factor", fx["factor"])
            self._add(fx)
        elif mode == "pixelate":
            fx.update(block=int(self.config_store.get("pixel_block") or 16), shape=self._pixel_shape,
                      radius=float(self.config_store.get("round_pixel")))
            self._add(fx)

    def add_image(self) -> None:
        if self.board.layout is None:
            self.show_layouts()
            return
        path = self.ask_image_file()
        if not path:
            return
        W, H = self.board.size
        source = overlays.load_logo(path)
        w = W * 0.3
        if source.height * w / source.width > H * 0.5:
            w = H * 0.5 * source.width / source.height
        fx = self._new_fx("image", image=path, w=int(w), opacity=1.0, radius=0.0, x=0, y=0)
        self._center_fx(fx, "x")
        self._center_fx(fx, "y")
        self._add(fx)

    def add_logo(self) -> None:
        if self.board.layout is None:
            self.show_layouts()
            return
        cfg = self.config_store
        path = str(cfg.get("logo_path") or "")
        text = str(cfg.get("operator_text") or "").strip()
        if overlays.load_logo(path) is None:
            path = ""
        if not path and not text:
            messagebox.showinfo(tr("Logo"), tr("Carica l'immagine del logo e scrivi il testo dell'operatore nella pagina "
                                               "Configura, poi premi di nuovo Logo."), self.app)
            return
        W, H = self.board.size
        fx = self._new_fx("logo", x=0, y=0, logo=path, w=max(8, int(round(W * float(cfg.get("logo_width") or 12) / 100))),
                          text=text, size=max(8, int(round(min(W, H) * float(cfg.get("operator_size") or 3.5) / 100))),
                          color=str(cfg.get("operator_color") or "#FFFFFF"), layout=str(cfg.get("logo_layout") or "right"),
                          shadow=True, font=default_font(), corner=str(cfg.get("logo_corner") or "bottom-right"),
                          bg=bool(cfg.get("logo_bg")), bg_color=str(cfg.get("logo_bg_color") or "#000000"),
                          bg_alpha=float(cfg.get("logo_bg_alpha")), bg_radius=float(cfg.get("logo_bg_radius")))
        self.place_logo(fx)
        self._add(fx)

    def delete_selection(self) -> None:
        if self.selected_kind == "effect":
            self.delete_effect(self.selected_id)
        elif self.selected_kind == "cell" and self.board.image_of(self.selected_id) is not None:
            self.clear_cell(self.selected_id)

    # ------------------------------------------------------------- uscita

    def _final_image(self) -> Image.Image | None:
        if self.board.layout is None or not any(c.get("image") for c in self.board.cells):
            messagebox.showinfo(tr("Immagini"), tr("Il foglio e' vuoto: carica almeno un'immagine."), self.app)
            return None
        return self.board.render(1.0)

    def export(self) -> None:
        image = self._final_image()
        if image is None:
            return
        path = filedialog.asksaveasfilename(title=tr("Esporta immagine"), parent=self, defaultextension=".png",
                                            initialdir=self.config_store.get("last_export_dir") or None,
                                            initialfile="immagine.png",
                                            filetypes=[(tr("Immagine PNG"), "*.png"), (tr("Immagine JPG"), "*.jpg *.jpeg")])
        if not path:
            return
        try:
            if path.lower().endswith((".jpg", ".jpeg")):
                image.convert("RGB").save(path, "JPEG", quality=92)
            else:
                image.save(path, "PNG")
        except OSError as exc:
            messagebox.showerror(tr("Esporta immagine"), str(exc), self.app)
            return
        self.config_store.set("last_export_dir", os.path.dirname(path))
        self.config_store.save()
        self.status(tr("Immagine salvata: {path} ({width} x {height} px)").format(
            path=path, width=image.width, height=image.height))

    def copy_to_clipboard(self) -> None:
        image = self._final_image()
        if image is None:
            return
        if winshell.copy_image(image):
            self.status(tr("Foglio copiato negli appunti ({width} x {height} px).").format(width=image.width,
                                                                                         height=image.height))
        else:
            self.status(tr("Impossibile copiare negli appunti."))

    def markers(self) -> list[dict]:
        """I punti numerati in ordine: prima i numeri, poi le lettere."""
        def order(fx):
            label = str(fx.get("label") or "")
            if fx.get("style") == "letter":
                return 1, len(label), label, 0
            digits = "".join(ch for ch in label if ch.isdigit())
            return 0, 0, "", int(digits) if digits else 0
        return sorted((fx for fx in self.project.effects if fx["type"] == "marker"), key=order)

    def caption_intro(self) -> str:
        """Il testo della didascalia scritto nel pannello del foglio, su una riga."""
        return " ".join(str(self.board.caption or "").split())

    def caption_lines(self) -> list[str]:
        """Le voci della didascalia: "1) nota" per ogni punto con una nota."""
        out = []
        for fx in self.markers():
            note = " ".join(str(fx.get("note") or "").split())
            if note:
                out.append(f"{fx.get('label', '')}) {note}")
        return out

    def copy_for_word(self) -> None:
        """Immagine e didascalia nel documento Word aperto, dove c'e' il cursore (la didascalia la crea Word)."""
        if self._word_busy:
            return
        image = self._final_image()
        if image is None:
            return
        lines = self.caption_lines()
        intro = self.caption_intro()
        label = tr("Figura")
        self._word_busy = True
        self.status(tr("Inserimento in Word..."))

        def work() -> None:
            result = wordcopy.insert(image, label, lines, intro)
            self.app.post(self._word_done, result, image, label, lines, intro)

        threading.Thread(target=work, daemon=True).start()

    def _word_done(self, result: tuple[bool, str, str], image: Image.Image, label: str, lines: list[str],
                   intro: str) -> None:
        self._word_busy = False
        ok, document, detail = result
        if ok:
            self.status(tr("Inserita in Word ({document}): {caption}").format(document=document, caption=detail))
            return
        # Word assente o occupato: restano gli appunti (la didascalia dipende da come Word incolla)
        if winshell.copy_rich(wordcopy.rtf(image, label, lines, intro), wordcopy.text(label, lines, intro)):
            self.status(tr("Word non risponde ({error}): immagine e didascalia copiate negli appunti, da incollare in "
                           "Word.").format(error=detail))
        else:
            self.status(tr("Impossibile copiare negli appunti."))

    # ------------------------------------------------------------- file del progetto

    def _state(self) -> str:
        """Il contenuto del progetto, da confrontare con quello salvato."""
        board = self.board
        return json.dumps({"layout": board.layout, "format": board.format, "gap": board.gap, "bg": board.bg,
                           "caption": board.caption, "cells": board.cells, "effects": board.project.effects},
                          sort_keys=True, default=str)

    def is_dirty(self) -> bool:
        board = self.board
        empty = not board.project.effects and not any(c.get("image") for c in board.cells)
        return self._state() != self._saved_state and not (empty and self.path is None)

    def save_project(self, ask: bool = False) -> bool:
        path = self.path
        if ask or not path:
            start = self.config_store.get("last_images_project_dir") or None
            path = filedialog.asksaveasfilename(
                title=tr("Salva progetto di immagini"), parent=self, defaultextension=".json", initialdir=start,
                initialfile=os.path.basename(self.path) if self.path else "immagini.json",
                filetypes=[(tr("Progetto immagini EditSimple (JSON)"), "*.json")])
            if not path:
                return False
        try:
            self.board.save(path)
        except OSError as exc:
            messagebox.showerror(tr("Salva progetto di immagini"), str(exc), self.app)
            return False
        self.path = path
        self._saved_state = self._state()
        self.project.dirty = False
        self.config_store.set("last_images_project_dir", os.path.dirname(path))
        self.status(tr("Progetto salvato: {path} (con la cartella {folder})").format(
            path=path, folder=os.path.splitext(os.path.basename(path))[0] + "_file"))
        return True

    def confirm_discard(self) -> bool:
        """True se si puo' lasciare il progetto (salvato, o l'utente non vuole salvarlo)."""
        if not self.is_dirty():
            return True
        answer = messagebox.askyesnocancel(tr("Immagini non salvate"),
                                           tr("Salvare le modifiche al progetto di immagini?"), self.app,
                                           yes=tr("Salva"), no=tr("Non salvare"))
        if answer is None:
            return False
        return self.save_project() if answer else True

    def open_project(self) -> None:
        if not self.confirm_discard():
            return
        path = filedialog.askopenfilename(title=tr("Apri progetto di immagini"), parent=self,
                                          initialdir=self.config_store.get("last_images_project_dir") or None,
                                          filetypes=[(tr("Progetto immagini EditSimple (JSON)"), "*.json"),
                                                     (tr("Tutti i file"), "*.*")])
        if path:
            self.load_project(path)

    def load_project(self, path: str) -> bool:
        try:
            board = Board.load(path)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            messagebox.showerror(tr("Apri progetto di immagini"),
                                 tr("Impossibile aprire il progetto:\n{error}").format(error=exc), self.app)
            return False
        self.cancel_mode()
        self.board = board
        self.path = path
        self.undo_stack.clear()
        self.redo_stack.clear()
        self._saved_state = self._state()
        self.config_store.set("last_images_project_dir", os.path.dirname(path))
        self.hide_layouts()
        self.select(None, None)
        self.refresh()
        self.status(tr("Progetto aperto: {path}").format(path=path))
        return True

    # ------------------------------------------------------------- tastiera

    def bind_keys(self) -> None:
        """Scorciatoie della pagina: le registra l'app dopo le sue (stesse lettere), aggiungendole."""
        top = self.app

        def on(handler, *args):
            def run(_event):
                if self.app._page != "image":
                    return None
                widget = self.focus_get()
                if isinstance(widget, (tk.Entry, tk.Text, ctk.CTkEntry, ctk.CTkTextbox)) or \
                        widget.__class__.__name__ in ("Entry", "Text"):
                    return None
                handler(*args)
                return "break"
            return run

        top.bind("<Control-v>", on(self.paste), add="+")
        top.bind("<Delete>", on(self.delete_selection), add="+")
        top.bind("<Escape>", on(self.cancel_mode), add="+")
        top.bind("<Control-z>", on(self.undo), add="+")
        top.bind("<Control-y>", on(self.redo), add="+")
        top.bind("<Control-s>", on(self.save_project), add="+")
        top.bind("<Control-S>", on(self.save_project, True), add="+")
        top.bind("<Control-o>", on(self.open_project), add="+")
        top.bind("<l>", on(self.add_logo), add="+")
        for key, mode in KEYS.items():
            top.bind(f"<{key}>", on(self.start_draw, mode), add="+")
