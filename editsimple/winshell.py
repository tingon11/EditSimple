# EditSimple — montaggio video per presentazioni.  Copyright (C) 2026 Andrea Cumini <andrea@osintinfo.net>
# SPDX-License-Identifier: GPL-3.0-only
# GNU GPL v3 con termini aggiuntivi (attribuzione dell'autore): vedi LICENSE e NOTICE.
"""File trascinati sulla finestra e immagini negli appunti (solo Windows, con ctypes).

Tk non riceve i file trascinati da Esplora risorse: la finestra del widget
viene registrata con DragAcceptFiles e il messaggio WM_DROPFILES si legge
sostituendo la sua procedura di finestra. Sugli altri sistemi le funzioni non
fanno nulla (il caricamento da file e Ctrl+V restano).
"""

from __future__ import annotations

import io
import sys
from typing import Callable

from PIL import Image

if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    _user32 = ctypes.windll.user32
    _shell32 = ctypes.windll.shell32
    _kernel32 = ctypes.windll.kernel32
    LRESULT = ctypes.c_ssize_t
    WNDPROC = ctypes.WINFUNCTYPE(LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
    WM_DROPFILES = 0x0233
    GWLP_WNDPROC = -4
    _user32.CallWindowProcW.argtypes = [ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
    _user32.CallWindowProcW.restype = LRESULT
    _user32.SetWindowLongPtrW.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_void_p]
    _user32.SetWindowLongPtrW.restype = ctypes.c_void_p
    _shell32.DragQueryFileW.argtypes = [ctypes.c_void_p, wintypes.UINT, ctypes.c_wchar_p, wintypes.UINT]
    _shell32.DragQueryFileW.restype = wintypes.UINT
    _shell32.DragQueryPoint.argtypes = [ctypes.c_void_p, ctypes.POINTER(wintypes.POINT)]
    _shell32.DragFinish.argtypes = [ctypes.c_void_p]
    _shell32.DragAcceptFiles.argtypes = [wintypes.HWND, wintypes.BOOL]
    _kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
    _kernel32.GlobalAlloc.restype = ctypes.c_void_p
    _kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    _kernel32.GlobalLock.restype = ctypes.c_void_p
    _kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    _kernel32.GlobalFree.argtypes = [ctypes.c_void_p]
    _user32.SetClipboardData.argtypes = [wintypes.UINT, ctypes.c_void_p]
    _user32.SetClipboardData.restype = ctypes.c_void_p
    _user32.OpenClipboard.argtypes = [wintypes.HWND]

_hooks: dict[int, tuple] = {}       # hwnd -> (procedura nuova, procedura vecchia): devono restare vive


def accept_files(widget, callback: Callable[[list[str], int, int], None]) -> bool:
    """Chiama `callback(percorsi, x, y)` (coordinate nel widget) quando si lasciano file sul widget."""
    if sys.platform != "win32":
        return False
    hwnd = widget.winfo_id()

    def proc(h, msg, wparam, lparam):
        if msg == WM_DROPFILES:
            count = _shell32.DragQueryFileW(wparam, 0xFFFFFFFF, None, 0)
            paths = []
            for i in range(count):
                length = _shell32.DragQueryFileW(wparam, i, None, 0)
                buffer = ctypes.create_unicode_buffer(length + 1)
                _shell32.DragQueryFileW(wparam, i, buffer, length + 1)
                paths.append(buffer.value)
            point = wintypes.POINT()
            _shell32.DragQueryPoint(wparam, ctypes.byref(point))
            _shell32.DragFinish(wparam)
            # qui si e' dentro il ciclo degli eventi di Tk: chiamare Tk ora fa cadere Python. Si mette in
            # coda e lo si consegna da un controllo periodico, fuori da questa procedura
            pending.append((paths, point.x, point.y))
            return 0
        return _user32.CallWindowProcW(_hooks[hwnd][1], h, msg, wparam, lparam)

    pending: list[tuple[list[str], int, int]] = []

    def deliver() -> None:
        while pending:
            paths, x, y = pending.pop(0)
            callback(paths, x, y)
        if widget.winfo_exists():
            widget.after(150, deliver)

    new_proc = WNDPROC(proc)
    old = _user32.SetWindowLongPtrW(hwnd, GWLP_WNDPROC, ctypes.cast(new_proc, ctypes.c_void_p))
    _hooks[hwnd] = (new_proc, old)
    _shell32.DragAcceptFiles(hwnd, True)
    widget.after(150, deliver)
    return True


def clipboard_image() -> tuple[Image.Image | None, str]:
    """L'immagine negli appunti (uno screenshot, o il primo file immagine copiato) e il suo nome."""
    from PIL import ImageGrab
    try:
        content = ImageGrab.grabclipboard()
    except (OSError, NotImplementedError):
        return None, ""
    if isinstance(content, Image.Image):
        return content, ""
    if isinstance(content, list):
        for path in content:
            try:
                image = Image.open(path)
                image.load()
                return image, path
            except (OSError, ValueError):
                continue
    return None, ""


def copy_image(image: Image.Image) -> bool:
    """Mette l'immagine negli appunti di Windows (formato DIB, quello che incollano tutti i programmi)."""
    if sys.platform != "win32":
        return False
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, "BMP")
    data = buffer.getvalue()[14:]                # senza l'intestazione del file BMP: resta il DIB
    CF_DIB, GMEM_MOVEABLE = 8, 0x0002
    handle = _kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
    if not handle:
        return False
    pointer = _kernel32.GlobalLock(handle)
    ctypes.memmove(pointer, data, len(data))
    _kernel32.GlobalUnlock(handle)
    if not _user32.OpenClipboard(None):
        _kernel32.GlobalFree(handle)
        return False
    try:
        _user32.EmptyClipboard()
        if not _user32.SetClipboardData(CF_DIB, handle):
            _kernel32.GlobalFree(handle)
            return False
    finally:
        _user32.CloseClipboard()
    return True                                  # da qui la memoria e' degli appunti


def _global(data: bytes):
    handle = _kernel32.GlobalAlloc(0x0002, len(data))          # GMEM_MOVEABLE
    if handle:
        pointer = _kernel32.GlobalLock(handle)
        ctypes.memmove(pointer, data, len(data))
        _kernel32.GlobalUnlock(handle)
    return handle


def copy_rich(rtf: bytes, text: str) -> bool:
    """Testo formattato (RTF, con immagini dentro) e la sua versione semplice negli appunti di Windows."""
    if sys.platform != "win32":
        return False
    _user32.RegisterClipboardFormatW.argtypes = [wintypes.LPCWSTR]
    _user32.RegisterClipboardFormatW.restype = wintypes.UINT
    CF_UNICODETEXT = 13
    formats = [(_user32.RegisterClipboardFormatW("Rich Text Format"), rtf + b"\0"),
               (CF_UNICODETEXT, (text + "\0").encode("utf-16-le"))]
    if not _user32.OpenClipboard(None):
        return False
    try:
        _user32.EmptyClipboard()
        for fmt, data in formats:
            handle = _global(data)
            if not handle or not _user32.SetClipboardData(fmt, handle):
                if handle:
                    _kernel32.GlobalFree(handle)
                return False
    finally:
        _user32.CloseClipboard()
    return True
