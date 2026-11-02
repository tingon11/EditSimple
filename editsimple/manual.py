# EditSimple — montaggio video per presentazioni.  Copyright (C) 2026 Andrea Cumini <andrea@osintinfo.net>
# SPDX-License-Identifier: GPL-3.0-only
# GNU GPL v3 con termini aggiuntivi (attribuzione dell'autore): vedi LICENSE e NOTICE.
"""La finestra del manuale d'uso: docs/manual/manual.<lingua>.md letto e impaginato nello stile del programma.

Il manuale e' in Markdown (titoli, elenchi, tabelle, immagini, link); qui viene
reso in un tk.Text con i caratteri e i colori del tema, con l'indice dei
capitoli a sinistra e la scelta della lingua in alto. Nell'eseguibile la
cartella docs/manual e' dentro il bundle (vedi scripts/build_exe.py).
"""

from __future__ import annotations

import re
import sys
import tkinter as tk
import webbrowser
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageTk

from . import i18n, theme, widgets
from .i18n import tr

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
MANUAL_DIR = ROOT / "docs" / "manual"
ONLINE = "https://github.com/tingon11/EditSimple/tree/main/docs/manual"
IMAGE_WIDTH = 860          # larghezza delle figure nel testo (le immagini del manuale sono larghe 1600 px)

_INLINE = re.compile(r"(!?\[[^\]]*\]\([^)]+\))|(\*\*[^*]+\*\*)|(\*[^*]+\*)|(`[^`]+`)")


def manual_path(lang: str) -> Path | None:
    """Il file del manuale nella lingua chiesta, o in inglese, o in italiano; None se non c'e'."""
    for code in (lang, "en", "it"):
        path = MANUAL_DIR / f"manual.{code}.md"
        if path.exists():
            return path
    return None


class ManualWindow(ctk.CTkToplevel):
    def __init__(self, parent, fonts: theme.Fonts) -> None:
        super().__init__(parent)
        self.fonts = fonts
        self.lang = i18n.language()
        self.title(tr("Manuale d'uso") + " - EditSimple")
        self.configure(fg_color=theme.BG)
        self.minsize(900, 600)
        self.transient(parent)             # resta sopra la finestra principale (non sopra tutto)
        widgets.style_dialog(self, logo=False)
        self._photos: list = []            # le immagini restano referenziate finche' la finestra vive
        self._marks: dict[str, str] = {}   # ancora del titolo -> nome del mark nel testo
        self._toc_buttons: list = []
        ui = theme.ui_font()
        mono = theme.mono_font()

        top = ctk.CTkFrame(self, fg_color=theme.PANEL, corner_radius=0)
        top.pack(fill="x")
        image = theme.logo(11)
        if image is not None:
            ctk.CTkLabel(top, text="", image=image, anchor="w").pack(side="left", padx=16, pady=10)
        self._title = ctk.CTkLabel(top, text=tr("Manuale d'uso"), font=fonts.page, text_color=theme.TEXT)
        self._title.pack(side="left", padx=(0, 16))
        names = dict(i18n.LANGUAGES)
        self._lang_var = tk.StringVar(value=names.get(self.lang, self.lang))
        ctk.CTkOptionMenu(top, variable=self._lang_var, values=list(names.values()), width=150, height=28,
                          font=fonts.body, command=lambda name: self.load(next((c for c, n in names.items() if n == name),
                                                                                self.lang))).pack(side="right", padx=16, pady=10)
        ctk.CTkLabel(top, text=tr("Lingua"), font=fonts.small, text_color=theme.TEXT_SOFT).pack(side="right")

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        self.toc = ctk.CTkScrollableFrame(body, width=250, fg_color=theme.PANEL, corner_radius=0,
                                          label_text=tr("Indice"), label_font=fonts.caption,
                                          label_text_color=theme.TEXT_FAINT, label_fg_color=theme.PANEL)
        self.toc.pack(side="left", fill="y")
        page = ctk.CTkFrame(body, fg_color=theme.BG, corner_radius=0)
        page.pack(side="left", fill="both", expand=True)
        self.text = tk.Text(page, bg=theme.BG, fg=theme.TEXT, wrap="word", padx=28, pady=18, borderwidth=0,
                            highlightthickness=0, cursor="arrow", font=(ui, 12), spacing1=2, spacing3=4,
                            insertwidth=0, selectbackground=theme.SELECT_BG, inactiveselectbackground=theme.SELECT_BG)
        bar = ctk.CTkScrollbar(page, command=self.text.yview)
        bar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)
        self.text.configure(yscrollcommand=bar.set)
        t = self.text
        t.tag_configure("h1", font=(ui, 22, "bold"), foreground=theme.TEXT, spacing1=10, spacing3=8)
        t.tag_configure("h2", font=(ui, 17, "bold"), foreground=theme.ACCENT, spacing1=22, spacing3=6)
        t.tag_configure("h3", font=(ui, 14, "bold"), foreground=theme.TEXT, spacing1=14, spacing3=4)
        t.tag_configure("p", lmargin1=0, lmargin2=0)
        t.tag_configure("bold", font=(ui, 12, "bold"))
        t.tag_configure("italic", font=(ui, 12, "italic"))
        t.tag_configure("code", font=(mono, 11), foreground=theme.OK, background=theme.PANEL)
        t.tag_configure("pre", font=(mono, 11), foreground=theme.TEXT_SOFT, background=theme.PANEL,
                        lmargin1=16, lmargin2=16, rmargin=16, spacing1=4, spacing3=4)
        t.tag_configure("quote", foreground=theme.TEXT_SOFT, lmargin1=18, lmargin2=18, rmargin=24,
                        font=(ui, 12, "italic"))
        t.tag_configure("li", lmargin1=18, lmargin2=36)
        t.tag_configure("row", lmargin1=10, lmargin2=28, spacing1=1, spacing3=1)
        t.tag_configure("cell", font=(ui, 12, "bold"), foreground=theme.TEXT_SOFT)
        t.tag_configure("dim", foreground=theme.TEXT_DIM)
        t.tag_configure("caption", foreground=theme.TEXT_DIM, font=(ui, 11, "italic"), spacing3=10)
        t.tag_configure("link", foreground=theme.ACCENT, underline=True)
        t.tag_bind("link", "<Enter>", lambda _e: t.configure(cursor="hand2"))
        t.tag_bind("link", "<Leave>", lambda _e: t.configure(cursor="arrow"))
        t.tag_configure("rule", font=(ui, 2), background=theme.BORDER)
        self.bind("<Escape>", lambda _e: self.destroy())
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.load(self.lang)
        self.update_idletasks()
        width = min(1240, max(900, parent.winfo_width() - 80))
        height = min(900, max(600, parent.winfo_height() - 60))
        widgets._place(self, parent, width, height)
        self.after(300, self.lift)         # customtkinter la rimostra poco dopo: torna davanti all'app

    # ------------------------------------------------------------------ caricamento

    def load(self, lang: str) -> None:
        """Mostra il manuale nella lingua `lang` (o in inglese, o in italiano se manca)."""
        self.lang = lang
        self._lang_var.set(dict(i18n.LANGUAGES).get(lang, lang))
        path = manual_path(lang)
        t = self.text
        t.configure(state="normal")
        t.delete("1.0", "end")
        self._photos.clear()
        self._marks.clear()
        for item in self._toc_buttons:
            item.destroy()
        self._toc_buttons.clear()
        if path is None:
            t.insert("end", tr("Il manuale non e' incluso in questa copia del programma.") + "\n\n", "h3")
            t.insert("end", tr("Si legge in linea su GitHub:") + " ")
            self._link(ONLINE, ONLINE)
            t.configure(state="disabled")
            return
        self._render(path.read_text(encoding="utf-8"), path.parent)
        t.configure(state="disabled")
        t.yview_moveto(0.0)

    def _render(self, source: str, base: Path) -> None:
        t = self.text
        lines = source.split("\n")
        i = 0
        paragraph: list[str] = []

        def flush() -> None:
            if paragraph:
                self._inline(" ".join(s.strip() for s in paragraph), base, ("p",))
                t.insert("end", "\n\n")
                paragraph.clear()

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if stripped.startswith("```"):
                flush()
                i += 1
                block = []
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    block.append(lines[i])
                    i += 1
                t.insert("end", "\n".join(block) + "\n", "pre")
                t.insert("end", "\n")
            elif stripped.startswith("#"):
                flush()
                level = len(stripped) - len(stripped.lstrip("#"))
                title = stripped[level:].strip()
                tag = "h1" if level == 1 else "h2" if level == 2 else "h3"
                mark = f"h{len(self._marks)}"
                t.mark_set(mark, "end-1c")
                t.mark_gravity(mark, "left")
                self._marks[_slug(title)] = mark
                t.insert("end", title + "\n", tag)
                if level in (2, 3):
                    self._toc_add(title, mark, level)
            elif stripped.startswith("!["):
                flush()
                self._image(stripped, base)
            elif stripped.startswith(">"):
                flush()
                quote = []
                while i < len(lines) and lines[i].strip().startswith(">"):
                    quote.append(lines[i].strip()[1:].strip())
                    i += 1
                self._inline(" ".join(quote), base, ("quote",))
                t.insert("end", "\n\n")
                continue
            elif stripped.startswith("|"):
                flush()
                rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    if not all(set(c) <= set("-: ") for c in cells):
                        rows.append(cells)
                    i += 1
                self._table(rows, base)
                continue
            elif re.match(r"^\s*([-*]|\d+\.)\s+", line):
                flush()
                m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
                indent, bullet, text = m.group(1), m.group(2), m.group(3)
                parts = [text]
                i += 1
                while i < len(lines) and lines[i].strip() and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]) \
                        and not lines[i].strip().startswith(("#", "![", "|", "```")):
                    parts.append(lines[i].strip())
                    i += 1
                marker = "• " if bullet in "-*" else bullet + " "
                t.insert("end", marker, ("li", "dim"))
                self._inline(" ".join(parts), base, ("li",))
                t.insert("end", "\n")
                if i < len(lines) and not lines[i].strip():
                    t.insert("end", "\n")
                continue
            elif stripped in ("---", "***"):
                flush()
                t.insert("end", " \n", "rule")
                t.insert("end", "\n")
            elif not stripped:
                flush()
            else:
                paragraph.append(line)
            i += 1
        flush()

    def _toc_add(self, title: str, mark: str, level: int) -> None:
        item = ctk.CTkButton(self.toc, text=title, anchor="w", fg_color="transparent", hover_color=theme.HOVER,
                             text_color=theme.TEXT_SOFT if level == 2 else theme.TEXT_DIM,
                             font=self.fonts.small, height=24, corner_radius=3,
                             command=lambda m=mark: self._goto(m))
        item.pack(fill="x", padx=(4 if level == 2 else 18, 4), pady=0)
        self._toc_buttons.append(item)

    def _goto(self, mark: str) -> None:
        self.text.yview(mark)

    def _table(self, rows: list[list[str]], base: Path) -> None:
        """Una tabella come elenco: la prima colonna in grassetto, le altre di seguito."""
        t = self.text
        for n, cells in enumerate(rows):
            if n == 0 and len(rows) > 1:
                t.insert("end", "   |   ".join(cells) + "\n", ("row", "cell"))
                continue
            t.insert("end", "• ", ("row", "dim"))
            for k, cell in enumerate(cells):
                if k:
                    t.insert("end", "   —   " if k == 1 else "   ·   ", ("row", "dim"))
                self._inline(cell, base, ("row",) + (("bold",) if k == 0 else ()))
            t.insert("end", "\n")
        t.insert("end", "\n")

    def _image(self, line: str, base: Path) -> None:
        m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line)
        if not m:
            return
        alt, src = m.group(1), m.group(2)
        path = base / src
        t = self.text
        try:
            image = Image.open(path).convert("RGB")
        except OSError:
            t.insert("end", f"[{alt}]\n\n", "dim")
            return
        width = min(IMAGE_WIDTH, image.width)
        image = image.resize((width, round(image.height * width / image.width)), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image, master=t)
        self._photos.append(photo)
        t.image_create("end", image=photo, padx=0, pady=6)
        t.insert("end", "\n")
        if alt:
            t.insert("end", alt + "\n", "caption")
        t.insert("end", "\n")

    def _inline(self, text: str, base: Path, tags: tuple) -> None:
        """Testo con grassetto, corsivo, codice e link."""
        t = self.text
        pos = 0
        for m in _INLINE.finditer(text):
            if m.start() > pos:
                t.insert("end", text[pos:m.start()], tags)
            token = m.group(0)
            if token.startswith("!["):
                pass                                    # immagine in mezzo a una riga: non prevista
            elif token.startswith("["):
                link = re.match(r"\[([^\]]*)\]\(([^)]+)\)", token)
                self._link(link.group(1), link.group(2), tags)
            elif token.startswith("**"):
                self._inline(token[2:-2], base, tags + ("bold",))     # dentro ci possono essere link o codice
            elif token.startswith("*"):
                self._inline(token[1:-1], base, tags + ("italic",))
            else:
                t.insert("end", token[1:-1], tags + ("code",))
            pos = m.end()
        if pos < len(text):
            t.insert("end", text[pos:], tags)

    def _link(self, label: str, target: str, tags: tuple = ()) -> None:
        t = self.text
        name = f"link{len(self._photos)}_{t.index('end-1c').replace('.', '_')}"
        t.insert("end", label, tags + ("link", name))
        t.tag_bind(name, "<Button-1>", lambda _e, u=target: self._follow(u))

    def _follow(self, target: str) -> None:
        if target.startswith("#"):
            mark = self._marks.get(target[1:])
            if mark is not None:
                self._goto(mark)
            return
        m = re.match(r"manual\.([a-z]+)\.md$", target)
        if m:
            self.load(m.group(1))
            return
        if target.startswith(("http://", "https://")):
            webbrowser.open(target)


def _slug(title: str) -> str:
    """L'ancora di un titolo come la fa GitHub: minuscole, senza punteggiatura, spazi -> trattini."""
    s = re.sub(r"[^\w\- ]", "", title.strip().lower(), flags=re.UNICODE)
    return s.replace(" ", "-")
