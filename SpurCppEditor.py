import os, re, sys, queue, threading, subprocess, tkinter as tk
from tkinter import filedialog, font, messagebox
from PIL import Image, ImageTk
import shutil

# ─── COLOUR SCHEME ──────────────────────────────────────────────────────────
SPURS_BLUE   = "#132257"
SPURS_GREY   = "#d3d3d3"
COMMENT_GREY = "#7f8c8d"
STRING_ORANGE = "#e67e22"
NUMBER_BLUE  = "#5dade2"
KEYWORD_CYAN = "#a6cee3"

# ─── KEYWORDS (simple set) ──────────────────────────────────────────────────
KEYWORDS = {
    "int","float","double","char","void","bool","long","short","unsigned","signed",
    "if","else","while","for","do","switch","case","default","break","continue","return",
    "class","struct","public","private","protected","namespace","using","new","delete","this",
    "cout","cin","endl","main","auto","constexpr","nullptr","template","typename",
    "static","inline","virtual"
}

MAX_FILE_SIZE = 10*1024*1024  # 10 MB

# ─── Line-number gutter ─────────────────────────────────────────────────────
class LineNumbers(tk.Canvas):
    def __init__(self, text, **kw):
        super().__init__(text.master, **kw)
        self.text = text
        for ev in ("<KeyRelease>", "<MouseWheel>", "<Configure>", "<<Change>>"):
            text.bind(ev, self.redraw, add="+")
    def redraw(self, _=None):
        self.delete("all")
        try:
            i = self.text.index("@0,0")
        except tk.TclError:
            return
        while True:
            info = self.text.dlineinfo(i)
            if info is None: break
            y = info[1]
            ln = i.split(".")[0]
            self.create_text(2, y, anchor="nw", text=ln,
                             fill=SPURS_GREY, font=("Courier New", 10, "bold"))
            i = self.text.index(f"{i}+1line")

# ─── Console widget ─────────────────────────────────────────────────────────
class Console(tk.Text):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.config(bg=SPURS_BLUE, fg=SPURS_GREY, insertbackground=SPURS_GREY,
                    state="disabled", height=8, wrap="word",
                    font=("Courier New", 11))
        self.tag_config("error",   foreground="#e74c3c", font=("Courier New", 11, "bold"))
        self.tag_config("success", foreground="#2ecc71", font=("Courier New", 11, "bold"))
    def write(self, msg, tag=None):
        self.config(state="normal")
        self.insert("end", msg, tag)
        self.see("end")
        self.config(state="disabled")

# ─── Main editor window ─────────────────────────────────────────────────────
class SpurCEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SpurC++ Editor")
        self.geometry("1100x700")
        self.configure(bg=SPURS_BLUE)
        self.filename = None

        # icon
        try:
            ico = ImageTk.PhotoImage(Image.open("spurslogo.ico"))
            self.iconphoto(False, ico)
        except Exception:
            pass

        self.code_font = font.Font(family="Courier New", size=12)
        self._build_ui()
        self._bind_events()

    # ── UI -------------------------------------------------------------------
    def _build_ui(self):
        outer = tk.Frame(self, bg=SPURS_BLUE)
        outer.pack(fill="both", expand=True)

        # line numbers
        self.text = tk.Text(outer, bg=SPURS_BLUE, fg=SPURS_GREY,
                            insertbackground=SPURS_GREY, wrap="none",
                            undo=True, font=self.code_font, borderwidth=0)
        self.linenums = LineNumbers(self.text, width=40, bg=SPURS_BLUE,
                                    highlightthickness=0)
        self.linenums.pack(side="left", fill="y")

        self.text.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(outer, command=self.text.yview)
        sb.pack(side="right", fill="y")
        self.text.config(yscrollcommand=sb.set)

        # console
        self.console = Console(self)
        self.console.pack(fill="x")

        # status bar
        self.status = tk.Label(self, bg=SPURS_GREY, fg=SPURS_BLUE, anchor="w",
                               font=("Courier New", 9))
        self.status.pack(fill="x")
        self._update_status()

        # toolbar
        bar = tk.Frame(self, bg=SPURS_BLUE)
        bar.pack(fill="x")
        self._add_toolbar_button(bar, "Open",    self.open_file)
        self._add_toolbar_button(bar, "Save",    self.save_file)
        self._add_toolbar_button(bar, "Compile", self.compile)
        self._add_toolbar_button(bar, "Run",     self.run)

        tk.Button(bar, text="Toggle Console", bg=SPURS_GREY, fg=SPURS_BLUE,
                  font=("Courier New", 9), relief="flat",
                  command=self._toggle_console).pack(side="right", padx=4, pady=2)

        # syntax tags
        self.text.tag_config("comment", foreground=COMMENT_GREY,
                             font=("Courier New", 12, "italic"))
        self.text.tag_config("string",  foreground=STRING_ORANGE)
        self.text.tag_config("number",  foreground=NUMBER_BLUE)
        self.text.tag_config("keyword", foreground=KEYWORD_CYAN,
                             font=("Courier New", 12, "bold"))

    def _add_toolbar_button(self, parent, label, cmd):
        tk.Button(parent, text=label, command=cmd,
                  bg=SPURS_GREY, fg=SPURS_BLUE,
                  font=("Courier New", 9), relief="flat"
                  ).pack(side="left", padx=4, pady=2)

    # ── Syntax highlight -----------------------------------------------------
    def _highlight(self, _=None):
        code = self.text.get("1.0", "end-1c")
        for tag in ("comment","string","number","keyword"):
            self.text.tag_remove(tag,"1.0","end")

        for m in re.finditer(r'/\*[\s\S]*?\*/', code):
            self.text.tag_add("comment", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        for m in re.finditer(r'//.*', code):
            self.text.tag_add("comment", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        for m in re.finditer(r'"(\\.|[^"\\])*"', code):
            self.text.tag_add("string",  f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        for m in re.finditer(r'\b\d+(\.\d+)?\b', code):
            self.text.tag_add("number",  f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        for kw in KEYWORDS:
            for m in re.finditer(rf'\b{re.escape(kw)}\b', code):
                self.text.tag_add("keyword", f"1.0+{m.start()}c", f"1.0+{m.end()}c")

    # ── File operations ------------------------------------------------------
    def open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("C/C++ files","*.c *.cpp *.h *.hpp"),("All files","*.*")]
        )
        if not path: return
        if os.path.getsize(path) > MAX_FILE_SIZE:
            messagebox.showerror("Too large","File exceeds 10 MB.")
            return
        try:
            with open(path,"r",encoding="utf-8") as f:
                data = f.read()
            self.text.delete("1.0","end")
            self.text.insert("1.0", data)
            self.filename = path
            self.title(f"{os.path.basename(path)} • SpurC Editor")
            self._highlight()
        except Exception as e:
            self.console.write(f"Open error: {e}\n","error")

    def save_file(self):
        if not self.filename:
            self.filename = filedialog.asksaveasfilename(
                defaultextension=".cpp",
                filetypes=[("C++ files","*.cpp"),("C files","*.c"),("All files","*.*")]
            )
        if self.filename:
            try:
                with open(self.filename,"w",encoding="utf-8") as f:
                    f.write(self.text.get("1.0","end-1c"))
                self.console.write("Saved successfully\n","success")
            except Exception as e:
                self.console.write(f"Save error: {e}\n","error")

    # ── Compile / Run --------------------------------------------------------
    def compile(self):
        if not self.filename:
            messagebox.showerror("Error", "Save file first.")
            return
        exe = os.path.splitext(self.filename)[0] + ".exe"
        compiler = shutil.which("g++") if self.filename.endswith(".cpp") else shutil.which("gcc")
        if not compiler:
            messagebox.showerror("Error", "Compiler not found.")
            return
        cmd = [compiler, self.filename, "-o", exe]

        def run_compile():
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()
            output = out.decode() + err.decode()
            if proc.returncode == 0:
                messagebox.showinfo("Success", "Compilation succeeded.")
                self.console.write("Compilation succeeded.\n","success")
            else:
                messagebox.showerror("Error", f"Compilation failed:\n{output}")
                self.console.write(f"Compilation failed:\n{output}\n","error")

        threading.Thread(target=run_compile).start()

    def run(self):
        if not self.filename:
            messagebox.showerror("Error", "Save and compile file first.")
            return
        exe = os.path.splitext(self.filename)[0] + ".exe"
        if not os.path.exists(exe):
            messagebox.showerror("Error", "Executable not found. Compile first.")
            return

        try:
            subprocess.Popen(['start', 'cmd', '/k', exe], shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run executable:\n{e}")

    # ── Other UI updates -----------------------------------------------------
    def _update_status(self, _=None):
        length = len(self.text.get("1.0", "end-1c"))
        self.status.config(text=f"Length: {length} chars")

    def _toggle_console(self):
        if self.console.winfo_viewable():
            self.console.pack_forget()
        else:
            self.console.pack(fill="x")

    def _bind_events(self):
        self.text.bind("<KeyRelease>", self._highlight)
        self.text.bind("<<Change>>", self.linenums.redraw)
        self.text.bind("<Configure>", self.linenums.redraw)
        self.text.bind("<KeyRelease>", self._update_status)

if __name__ == "__main__":
    app = SpurCEditor()
    app.mainloop()
