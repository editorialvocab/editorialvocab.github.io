"""
vocab_gui.py  ─  Editorial Vocab PDF Generator  (GUI Launcher)
──────────────────────────────────────────────────────────────
Place this file in the SAME folder as:
  • generate_cards_pdf.py
  • generate_10vocab.py

Run:
  python vocab_gui.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import subprocess
import threading
import sys
import os
import calendar
from pathlib import Path

# ─── Branding / colours ───────────────────────────────────────────────────────
THEMES = {
    "EnToBn": {
        "primary":   "#C62828",
        "light":     "#FFEBEE",
        "pill":      "#E53935",
        "tag":       "🇧🇩 Daily Star (Bengali)",
        "handle":    "editorialvocabappbd",
    },
    "EnToHn": {
        "primary":   "#1A237E",
        "light":     "#E8EAF6",
        "pill":      "#283593",
        "tag":       "🇮🇳 The Hindu (Hindi)",
        "handle":    "editorialvocabapp",
    },
}
BG        = "#F4F6F9"
PANEL     = "#FFFFFF"
BORDER    = "#D9DEE8"
TEXT      = "#1A1A2E"
SUBTEXT   = "#6B7280"
SUCCESS   = "#16A34A"
WARN      = "#D97706"
FONT_FAM  = "Segoe UI"          # falls back gracefully on non-Windows
SCRIPT_DIR = Path(__file__).resolve().parent


# ─── Utility: run a subprocess and stream output to a Text widget ─────────────
def run_script(cmd: list[str], console: scrolledtext.ScrolledText,
               on_done, on_error):
    """Runs cmd in a thread, streams stdout/stderr to console widget."""
    def target():
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=str(SCRIPT_DIR),
            )
            for line in process.stdout:
                console.after(0, _append, console, line)
            process.wait()
            if process.returncode == 0:
                console.after(0, _append, console,
                              "\n✅  Done! PDF generated successfully.\n", "ok")
                console.after(0, on_done)
            else:
                console.after(0, _append, console,
                              f"\n❌  Process exited with code {process.returncode}\n", "err")
                console.after(0, on_error)
        except Exception as exc:
            console.after(0, _append, console, f"\n❌  {exc}\n", "err")
            console.after(0, on_error)

    threading.Thread(target=target, daemon=True).start()


def _append(console: scrolledtext.ScrolledText, text: str, tag: str = ""):
    console.configure(state="normal")
    console.insert(tk.END, text, tag)
    console.see(tk.END)
    console.configure(state="disabled")


# ─── Reusable widgets ─────────────────────────────────────────────────────────
def make_label(parent, text, size=10, bold=False, color=TEXT, **kw):
    font = (FONT_FAM, size, "bold" if bold else "normal")
    return tk.Label(parent, text=text, font=font, fg=color,
                    bg=parent["bg"] if "bg" in parent.keys() else PANEL, **kw)


def make_entry(parent, textvariable=None, width=38, **kw):
    e = tk.Entry(parent, textvariable=textvariable, width=width,
                 font=(FONT_FAM, 10), relief="flat",
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor="#7C83FD", **kw)
    return e


def make_button(parent, text, command, color="#4F46E5",
                fg="#FFFFFF", width=None, **kw):
    kw_btn = dict(text=text, command=command, font=(FONT_FAM, 10, "bold"),
                  bg=color, fg=fg, activebackground=color,
                  activeforeground=fg, relief="flat", cursor="hand2",
                  padx=14, pady=7, bd=0)
    if width:
        kw_btn["width"] = width
    kw_btn.update(kw)
    b = tk.Button(parent, **kw_btn)

    def on_enter(e): b.config(bg=_darken(color))
    def on_leave(e): b.config(bg=color)
    b.bind("<Enter>", on_enter)
    b.bind("<Leave>", on_leave)
    return b


def _darken(hex_color: str, factor=0.85) -> str:
    hc = hex_color.lstrip("#")
    r, g, b = int(hc[0:2], 16), int(hc[2:4], 16), int(hc[4:6], 16)
    return f"#{int(r*factor):02X}{int(g*factor):02X}{int(b*factor):02X}"


def card_frame(parent, title: str, **kw) -> tk.LabelFrame:
    lf = tk.LabelFrame(
        parent, text=f"  {title}  ",
        font=(FONT_FAM, 9, "bold"), fg=SUBTEXT,
        bg=PANEL, bd=1, relief="groove",
        padx=10, pady=8, **kw
    )
    return lf


# ─── Type selector row (shared) ───────────────────────────────────────────────
def make_type_selector(parent, var: tk.StringVar, on_change=None) -> tk.Frame:
    row = tk.Frame(parent, bg=PANEL)
    make_label(row, "Vocabulary Type:", bold=True).pack(side="left", padx=(0, 12))
    for val, label, color in [
        ("EnToBn", "🇧🇩  Daily Star  (Bengali)", THEMES["EnToBn"]["pill"]),
        ("EnToHn", "🇮🇳  The Hindu  (Hindi)",    THEMES["EnToHn"]["pill"]),
    ]:
        rb = tk.Radiobutton(
            row, text=label, variable=var, value=val,
            font=(FONT_FAM, 10, "bold"), fg=color, bg=PANEL,
            selectcolor=PANEL, activebackground=PANEL,
            cursor="hand2",
            command=on_change,
        )
        rb.pack(side="left", padx=8)
    return row


# ─── Repo-root / output row ───────────────────────────────────────────────────
def make_path_row(parent, label: str, var: tk.StringVar,
                  mode="dir") -> tk.Frame:
    row = tk.Frame(parent, bg=PANEL)
    make_label(row, label, color=SUBTEXT).pack(side="left", padx=(0, 6))
    make_entry(row, textvariable=var, width=34).pack(side="left")

    def browse():
        if mode == "dir":
            p = filedialog.askdirectory(title=f"Select {label}")
        else:
            p = filedialog.asksaveasfilename(
                title="Save PDF as", defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")])
        if p:
            var.set(p)

    make_button(row, "Browse…", browse, color="#6B7280",
                pady=4, padx=8).pack(side="left", padx=6)
    return row


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — Monthly Cards PDF
# ══════════════════════════════════════════════════════════════════════════════
class MonthlyTab(tk.Frame):

    def __init__(self, parent, console, set_busy, set_idle):
        super().__init__(parent, bg=BG)
        self._console  = console
        self._set_busy = set_busy
        self._set_idle = set_idle
        self._build()

    def _build(self):
        pad = dict(padx=12, pady=6, sticky="ew")

        # ── Type ──────────────────────────────────────────────────────────────
        top = card_frame(self, "📋  Vocabulary Type")
        top.pack(fill="x", padx=14, pady=(14, 6))
        self._type = tk.StringVar(value="EnToBn")
        make_type_selector(top, self._type, self._on_type_change).pack(
            anchor="w", pady=4)

        # ── Date ──────────────────────────────────────────────────────────────
        date_f = card_frame(self, "📅  Month & Year")
        date_f.pack(fill="x", padx=14, pady=6)

        row = tk.Frame(date_f, bg=PANEL)
        row.pack(anchor="w")

        make_label(row, "Month:", bold=True).grid(row=0, column=0,
                                                   padx=(0, 8), sticky="w")
        self._month = tk.StringVar(value=calendar.month_name[1])
        month_cb = ttk.Combobox(row, textvariable=self._month, width=13,
                                 values=list(calendar.month_name)[1:],
                                 state="readonly", font=(FONT_FAM, 10))
        month_cb.grid(row=0, column=1, padx=(0, 20))

        make_label(row, "Year:", bold=True).grid(row=0, column=2,
                                                  padx=(0, 8), sticky="w")
        self._year = tk.StringVar(value="2025")
        year_vals  = [str(y) for y in range(2022, 2031)]
        year_cb    = ttk.Combobox(row, textvariable=self._year, width=7,
                                  values=year_vals, font=(FONT_FAM, 10))
        year_cb.grid(row=0, column=3)

        # ── Options ───────────────────────────────────────────────────────────
        opt_f = card_frame(self, "⚙️  Page Options  (uncheck to skip)")
        opt_f.pack(fill="x", padx=14, pady=6)

        self._cover    = tk.BooleanVar(value=True)
        self._index    = tk.BooleanVar(value=True)
        self._revision = tk.BooleanVar(value=True)
        self._mcq      = tk.BooleanVar(value=True)

        opts_row = tk.Frame(opt_f, bg=PANEL)
        opts_row.pack(anchor="w")
        for col, (label, var, color) in enumerate([
            ("📄 Cover Page",       self._cover,    "#6D28D9"),
            ("📋 Index Page",       self._index,    "#0369A1"),
            ("📖 Weekly Revision",  self._revision, "#059669"),
            ("📝 Final MCQ Test",   self._mcq,      "#DC2626"),
        ]):
            tk.Checkbutton(
                opts_row, text=label, variable=var,
                font=(FONT_FAM, 10), fg=color, bg=PANEL,
                selectcolor=PANEL, activebackground=PANEL, cursor="hand2",
            ).grid(row=0, column=col, padx=10, pady=4, sticky="w")

        # ── Paths ─────────────────────────────────────────────────────────────
        path_f = card_frame(self, "📂  Paths  (optional)")
        path_f.pack(fill="x", padx=14, pady=6)
        self._repo_root = tk.StringVar()
        self._out_dir   = tk.StringVar()

        make_path_row(path_f, "Repo Root:", self._repo_root, "dir").pack(
            anchor="w", pady=3)
        make_path_row(path_f, "Output Dir:", self._out_dir, "dir").pack(
            anchor="w", pady=3)

        # ── Generate button ───────────────────────────────────────────────────
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=10)
        self._btn = make_button(btn_row, "▶  Generate Monthly Cards PDF",
                                self._run, width=36)
        self._btn.pack(side="left")

        # status badge
        self._status = make_label(btn_row, "", color=SUBTEXT)
        self._status.pack(side="left", padx=14)

    def _on_type_change(self):
        pass  # could update colours later

    def _run(self):
        month_num = str(list(calendar.month_name).index(self._month.get())).zfill(2)
        year      = self._year.get()
        date_str  = f"{month_num}-{year}"
        vtype     = self._type.get()

        cmd = [sys.executable, str(SCRIPT_DIR / "generate_cards_pdf.py"),
               "-t", vtype, date_str]

        if not self._cover.get():    cmd.append("--no-cover")
        if not self._index.get():    cmd.append("--no-index")
        if not self._revision.get(): cmd.append("--no-revision")
        if not self._mcq.get():      cmd.append("--no-mcq")

        rr = self._repo_root.get().strip()
        if rr:
            cmd += ["--repo-root", rr]

        # If output dir given, cd into it
        cwd = self._out_dir.get().strip() or str(SCRIPT_DIR)

        self._log_cmd(cmd)
        self._set_busy()
        self._status.config(text="⏳  Generating…", fg=WARN)
        self._btn.config(state="disabled")

        def on_done():
            self._set_idle()
            self._status.config(text="✅  Done!", fg=SUCCESS)
            self._btn.config(state="normal")

        def on_err():
            self._set_idle()
            self._status.config(text="❌  Error", fg="#DC2626")
            self._btn.config(state="normal")

        run_script(cmd, self._console, on_done, on_err)

    def _log_cmd(self, cmd):
        _append(self._console, "\n" + "─" * 60 + "\n")
        _append(self._console, "▶  " + " ".join(cmd) + "\n\n", "cmd")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — Master Vocab eBook
# ══════════════════════════════════════════════════════════════════════════════
class MasterTab(tk.Frame):

    LETTERS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def __init__(self, parent, console, set_busy, set_idle):
        super().__init__(parent, bg=BG)
        self._console  = console
        self._set_busy = set_busy
        self._set_idle = set_idle
        self._letter_vars: dict[str, tk.BooleanVar] = {
            l: tk.BooleanVar(value=False) for l in self.LETTERS
        }
        self._build()

    def _build(self):
        # ── Type ──────────────────────────────────────────────────────────────
        top = card_frame(self, "📋  Vocabulary Type")
        top.pack(fill="x", padx=14, pady=(14, 6))
        self._type = tk.StringVar(value="EnToBn")
        make_type_selector(top, self._type).pack(anchor="w", pady=4)

        # ── Filter mode ───────────────────────────────────────────────────────
        filter_f = card_frame(self, "🔍  Word Filter  (choose one mode)")
        filter_f.pack(fill="x", padx=14, pady=6)

        self._mode = tk.StringVar(value="all")
        modes = [
            ("all",    "📚  Full A–Z (entire master list)"),
            ("letter", "🔤  By Starting Letter(s)"),
            ("range",  "🔢  By Serial Number Range"),
        ]
        for val, label in modes:
            rb = tk.Radiobutton(
                filter_f, text=label, variable=self._mode, value=val,
                font=(FONT_FAM, 10, "bold"), fg=TEXT, bg=PANEL,
                selectcolor=PANEL, activebackground=PANEL, cursor="hand2",
                command=self._on_mode_change,
            )
            rb.pack(anchor="w", pady=2)

        # Letter grid
        self._letter_frame = tk.Frame(filter_f, bg=PANEL)
        self._letter_frame.pack(anchor="w", padx=20, pady=(4, 0))
        self._build_letter_grid()
        self._letter_lbl = make_label(
            filter_f,
            "Click letters to select. Tip: A+B+C = Vol 1 bundle",
            color=SUBTEXT, size=9)
        self._letter_lbl.pack(anchor="w", padx=20)

        # Range row
        self._range_frame = tk.Frame(filter_f, bg=PANEL)
        self._range_frame.pack(anchor="w", padx=20, pady=(4, 0))
        make_label(self._range_frame, "From #", bold=True).pack(side="left")
        self._start = tk.StringVar(value="1")
        tk.Spinbox(self._range_frame, textvariable=self._start,
                   from_=1, to=99999, width=7,
                   font=(FONT_FAM, 10)).pack(side="left", padx=6)
        make_label(self._range_frame, "To #", bold=True).pack(side="left", padx=(10, 0))
        self._end = tk.StringVar(value="2500")
        tk.Spinbox(self._range_frame, textvariable=self._end,
                   from_=1, to=99999, width=7,
                   font=(FONT_FAM, 10)).pack(side="left", padx=6)
        make_label(self._range_frame, "  (e.g. 1–2500 = Vol 1)",
                   color=SUBTEXT, size=9).pack(side="left")

        self._on_mode_change()   # set initial visibility

        # ── Layout & Options ──────────────────────────────────────────────────
        opt_f = card_frame(self, "⚙️  Layout & Options")
        opt_f.pack(fill="x", padx=14, pady=6)

        row1 = tk.Frame(opt_f, bg=PANEL)
        row1.pack(anchor="w")

        make_label(row1, "Cards / page:", bold=True).grid(
            row=0, column=0, padx=(0, 8), sticky="w")
        self._cpp = tk.StringVar(value="8")
        cpp_cb = ttk.Combobox(row1, textvariable=self._cpp, width=6,
                               values=[ "12","16","18","20"], state="readonly",
                               font=(FONT_FAM, 10))
        cpp_cb.grid(row=0, column=1, padx=(0, 20))
        make_label(row1, "(8 = 2×4, good balance)", color=SUBTEXT,
                   size=9).grid(row=0, column=2, sticky="w")

        row2 = tk.Frame(opt_f, bg=PANEL)
        row2.pack(anchor="w", pady=(8, 0))
        self._cover    = tk.BooleanVar(value=True)
        self._chapters = tk.BooleanVar(value=True)
        for label, var, color in [
            ("📄  Cover Page",          self._cover,    "#6D28D9"),
            ("🔤  A–Z Chapter Dividers", self._chapters, "#0369A1"),
        ]:
            tk.Checkbutton(
                row2, text=label, variable=var,
                font=(FONT_FAM, 10), fg=color, bg=PANEL,
                selectcolor=PANEL, activebackground=PANEL, cursor="hand2",
            ).pack(side="left", padx=10)

        # ── Paths ─────────────────────────────────────────────────────────────
        path_f = card_frame(self, "📂  Paths  (optional)")
        path_f.pack(fill="x", padx=14, pady=6)
        self._repo_root = tk.StringVar()
        self._out_file  = tk.StringVar()

        make_path_row(path_f, "Repo Root:  ", self._repo_root, "dir").pack(
            anchor="w", pady=3)
        make_path_row(path_f, "Output PDF:", self._out_file, "file").pack(
            anchor="w", pady=3)

        # ── Generate button ───────────────────────────────────────────────────
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=14, pady=10)
        self._btn = make_button(btn_row, "▶  Generate Master Vocab eBook",
                                self._run, color="#1A237E", width=36)
        self._btn.pack(side="left")
        self._status = make_label(btn_row, "", color=SUBTEXT)
        self._status.pack(side="left", padx=14)

    # ── Letter grid ───────────────────────────────────────────────────────────
    def _build_letter_grid(self):
        for i, letter in enumerate(self.LETTERS):
            var = self._letter_vars[letter]
            cb  = tk.Checkbutton(
                self._letter_frame, text=letter, variable=var,
                width=2,
                font=(FONT_FAM, 10, "bold"),
                fg="#1A237E", bg=PANEL,
                selectcolor="#DBEAFE",
                activebackground=PANEL,
                cursor="hand2",
            )
            cb.grid(row=i // 9, column=i % 9, padx=2, pady=2)

        # Quick-select buttons
        qs = tk.Frame(self._letter_frame, bg=PANEL)
        qs.grid(row=3, column=0, columnspan=9, sticky="w", pady=(6, 0))
        for label, letters in [
            ("A–G",  "ABCDEFG"),
            ("H–N",  "HIJKLMN"),
            ("O–U",  "OPQRSTU"),
            ("V–Z",  "VWXYZ"),
            ("All",  self.LETTERS),
            ("None", []),
        ]:
            make_button(
                qs, label,
                lambda ls=letters: self._quick_select(ls),
                color="#4F46E5", pady=3, padx=8,
            ).pack(side="left", padx=3)

    def _quick_select(self, letters):
        target = set(letters)
        for l, v in self._letter_vars.items():
            v.set(l in target)

    def _on_mode_change(self):
        mode = self._mode.get()
        if mode == "letter":
            self._letter_frame.pack(anchor="w", padx=20, pady=(4, 0))
            self._letter_lbl.pack(anchor="w", padx=20)
            self._range_frame.pack_forget()
        elif mode == "range":
            self._range_frame.pack(anchor="w", padx=20, pady=(4, 0))
            self._letter_frame.pack_forget()
            self._letter_lbl.pack_forget()
        else:
            self._letter_frame.pack_forget()
            self._letter_lbl.pack_forget()
            self._range_frame.pack_forget()

    def _run(self):
        vtype = self._type.get()
        cmd   = [sys.executable, str(SCRIPT_DIR / "generate_10vocab.py"),
                 "-t", vtype]

        mode = self._mode.get()
        if mode == "letter":
            selected = [l for l, v in self._letter_vars.items() if v.get()]
            if not selected:
                self._status.config(text="⚠  Select at least one letter!", fg=WARN)
                return
            cmd += ["--letter"] + selected
        elif mode == "range":
            try:
                s = int(self._start.get())
                e = int(self._end.get())
                if s > e:
                    raise ValueError
                cmd += ["--start", str(s), "--end", str(e)]
            except ValueError:
                self._status.config(text="⚠  Invalid range!", fg=WARN)
                return

        cmd += ["--cards-per-page", self._cpp.get()]
        if not self._cover.get():    cmd.append("--no-cover")
        if not self._chapters.get(): cmd.append("--no-chapters")

        rr = self._repo_root.get().strip()
        if rr:
            cmd += ["--repo-root", rr]

        of = self._out_file.get().strip()
        if of:
            cmd += ["--out", of]

        self._log_cmd(cmd)
        self._set_busy()
        self._status.config(text="⏳  Generating…", fg=WARN)
        self._btn.config(state="disabled")

        def on_done():
            self._set_idle()
            self._status.config(text="✅  Done!", fg=SUCCESS)
            self._btn.config(state="normal")

        def on_err():
            self._set_idle()
            self._status.config(text="❌  Error", fg="#DC2626")
            self._btn.config(state="normal")

        run_script(cmd, self._console, on_done, on_err)

    def _log_cmd(self, cmd):
        _append(self._console, "\n" + "─" * 60 + "\n")
        _append(self._console, "▶  " + " ".join(cmd) + "\n\n", "cmd")


# ══════════════════════════════════════════════════════════════════════════════
#  Main App Window
# ══════════════════════════════════════════════════════════════════════════════
class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Editorial Vocab PDF Generator")
        self.geometry("860x820")
        self.minsize(740, 700)
        self.configure(bg=BG)
        self.resizable(True, True)

        # Try to set a window icon (skip silently if unavailable)
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        self._build_header()
        self._build_tabs()
        self._build_console()
        self._build_statusbar()

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg="#1A1A2E", pady=14)
        hdr.pack(fill="x")

        tk.Label(hdr, text="📚  Editorial Vocab  PDF Generator",
                 font=(FONT_FAM, 16, "bold"), fg="#FFFFFF",
                 bg="#1A1A2E").pack(side="left", padx=20)

        # Social pills
        pill_frame = tk.Frame(hdr, bg="#1A1A2E")
        pill_frame.pack(side="right", padx=16)
        for label, color in [("▶ YT", "#FF0000"),
                              ("f  FB", "#1877F2"),
                              ("◈ IG", "#C13584")]:
            tk.Label(pill_frame, text=label,
                     font=(FONT_FAM, 9, "bold"), fg="#fff",
                     bg=color, padx=7, pady=3,
                     relief="flat").pack(side="left", padx=3)
        tk.Label(pill_frame, text="  @editorialvocabapp[bd]",
                 font=(FONT_FAM, 9), fg="#AAA",
                 bg="#1A1A2E").pack(side="left", padx=4)

    # ── Notebook tabs ─────────────────────────────────────────────────────────
    def _build_tabs(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Custom.TNotebook",          background=BG, borderwidth=0)
        style.configure("Custom.TNotebook.Tab",
                        font=(FONT_FAM, 10, "bold"),
                        padding=[18, 8],
                        background=BORDER,
                        foreground=SUBTEXT)
        style.map("Custom.TNotebook.Tab",
                  background=[("selected", PANEL)],
                  foreground=[("selected", "#1A1A2E")])

        nb = ttk.Notebook(self, style="Custom.TNotebook")
        nb.pack(fill="both", expand=False, padx=10, pady=(10, 0))

        self._tab1 = MonthlyTab(nb, None, self._set_busy, self._set_idle)
        self._tab2 = MasterTab(nb,  None, self._set_busy, self._set_idle)

        nb.add(self._tab1, text="📅  Monthly Cards PDF")
        nb.add(self._tab2, text="📖  Master Vocab eBook")

    # ── Console ───────────────────────────────────────────────────────────────
    def _build_console(self):
        con_frame = tk.LabelFrame(self,
                                   text="  📟  Console Output  ",
                                   font=(FONT_FAM, 9, "bold"), fg=SUBTEXT,
                                   bg=BG, bd=1, relief="groove",
                                   padx=6, pady=6)
        con_frame.pack(fill="both", expand=True, padx=10, pady=(6, 0))

        self._console = scrolledtext.ScrolledText(
            con_frame, height=12,
            font=("Consolas", 9),
            bg="#0D1117", fg="#C9D1D9",
            insertbackground="#C9D1D9",
            relief="flat", state="disabled",
            wrap="word",
        )
        self._console.pack(fill="both", expand=True)

        # Tags for coloured output
        self._console.tag_config("ok",  foreground="#3FB950")
        self._console.tag_config("err", foreground="#F85149")
        self._console.tag_config("cmd", foreground="#79C0FF", font=("Consolas", 9, "bold"))

        # Wire console into tabs
        self._tab1._console = self._console
        self._tab2._console = self._console

        # Clear button
        btn_row = tk.Frame(con_frame, bg=BG)
        btn_row.pack(fill="x", pady=(4, 0))
        make_button(btn_row, "🗑  Clear Console", self._clear_console,
                    color="#374151", pady=4, padx=10).pack(side="right")

        # Welcome message
        _append(self._console,
                "Welcome to Editorial Vocab PDF Generator!\n"
                "Select a tab above, configure your settings, then press Generate.\n\n",
                "ok")

    # ── Status bar ────────────────────────────────────────────────────────────
    def _build_statusbar(self):
        bar = tk.Frame(self, bg="#E5E7EB", height=26)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._progress = ttk.Progressbar(bar, mode="indeterminate", length=160)
        self._progress.pack(side="right", padx=10, pady=4)

        self._status_lbl = tk.Label(bar, text="Ready",
                                     font=(FONT_FAM, 9), fg=SUBTEXT,
                                     bg="#E5E7EB")
        self._status_lbl.pack(side="left", padx=10)

        scripts_ok = all(
            (SCRIPT_DIR / s).exists()
            for s in ["generate_cards_pdf.py", "generate_10vocab.py"]
        )
        info = (
            f"  ✅  Scripts found in {SCRIPT_DIR}"
            if scripts_ok
            else f"  ⚠️  Scripts NOT found in {SCRIPT_DIR} — place them alongside vocab_gui.py"
        )
        tk.Label(bar, text=info, font=(FONT_FAM, 8),
                 fg=SUCCESS if scripts_ok else "#DC2626",
                 bg="#E5E7EB").pack(side="left", padx=4)

    # ── Busy / idle helpers ───────────────────────────────────────────────────
    def _set_busy(self):
        self._progress.start(12)
        self._status_lbl.config(text="Generating PDF…", fg=WARN)

    def _set_idle(self):
        self._progress.stop()
        self._status_lbl.config(text="Ready", fg=SUBTEXT)

    def _clear_console(self):
        self._console.configure(state="normal")
        self._console.delete("1.0", tk.END)
        self._console.configure(state="disabled")


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()
