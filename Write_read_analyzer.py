import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk, font as tkfont
 
class SVUVMAnalyzerFast:
    def __init__(self, root):
        self.root = root
        self.root.title("SV/UVM Variable Access Viewer (Fast)")
        self.root.geometry("900x600")
 
        self.lines = []
        self.file_line_offsets = []
        self.current_file = None
        self.result_map = {}
 
        self.chunk_size = 1000  # lines to load at once in code_view
        self.loaded_lines = 0
 
        self.sv_keywords = [
            "module", "endmodule", "input", "output", "wire", "reg", "logic", "assign", "always",
            "begin", "end", "if", "else", "elseif", "case", "for", "while", "function", "endfunction",
            "task", "endtask", "class", "endclass", "virtual", "static", "extern", "bit", "int",
            "type_id", "extends", "get", "set", "super", "create", "$cast"
        ]
        self.uvm_keywords = [
            "uvm_component_utils", "uvm_object_utils", "uvm_config_db", "uvm_info", "uvm_error",
            "uvm_phase", "uvm_test", "uvm_env", "uvm_driver", "uvm_monitor", "uvm_agent",
            "uvm_sequence", "uvm_sequencer", "uvm_analysis_port", "uvm_analysis_imp",
            "uvm_subscriber", "uvm_factory", "uvm_top"
        ]
        self.pattern_sv = re.compile(r"\b(" + "|".join(re.escape(w) for w in self.sv_keywords) + r")\b")
        self.pattern_uvm = re.compile(r"\b(" + "|".join(re.escape(w) for w in self.uvm_keywords) + r")\b")
 
        # Default font and theme
        self.font_family = "Courier"
        self.font_size = 11
        self.theme = "light"
 
        # Result panel position options
        self.result_positions = ["bottom", "right", "left", "top"]
        self.result_pos_idx = 0  # start at bottom
 
        self.create_widgets()
        self.bind_shortcuts()
        self.create_menu()
        self.apply_theme()
 
    def create_widgets(self):
        top = tk.Frame(self.root)
        top.pack(fill="x", padx=5, pady=5)
 
        tk.Label(top, text="File or Folder:").pack(side="left")
        self.entry_path = tk.Entry(top, width=50)
        self.entry_path.pack(side="left", padx=5)
        self.entry_path.bind("<Return>", self.on_enter_path)
 
        tk.Button(top, text="Browse File", command=self.browse_file).pack(side="left", padx=2)
        tk.Button(top, text="Browse Folder", command=self.browse_folder).pack(side="left", padx=2)
 
        self.load_btn = tk.Button(top, text="Load", command=self.load_path)
        self.load_btn.pack(side="left", padx=10)
 
        # Paned window to allow resizing code/result areas
        self.paned = tk.PanedWindow(self.root, sashrelief=tk.RAISED)
        self.paned.pack(fill="both", expand=True)
 
        # Create code view and result view frames
        self.code_frame = tk.Frame(self.paned)
        self.result_frame = tk.Frame(self.paned, height=150)  # initial size hint
 
        self.code_view = scrolledtext.ScrolledText(self.code_frame, wrap="none", undo=True)
        ##self.code_view = scrolledtext.ScrolledText(self.root, wrap="none", undo=True)
        self.code_view.pack(fill="both", expand=True)
        self.code_view.config(font=(self.font_family, self.font_size))
        self.code_view.bind("<Button-1>", self.on_code_click)
        self.code_view.bind("<MouseWheel>", self.on_scroll)
        self.code_view.bind("<KeyRelease>", self.on_key_release)
 
        self.code_view.tag_config("keyword", foreground="blue", font=(self.font_family, self.font_size, "bold"))
        self.code_view.tag_config("uvm", foreground="darkgreen", font=(self.font_family, self.font_size, "bold"))
        self.code_view.tag_config("comment", foreground="gray", font=(self.font_family, self.font_size, "italic"))
        self.code_view.tag_config("string", foreground="brown")
        self.code_view.tag_config("highlight", background="yellow")
        self.code_view.tag_config("search", background="lightblue")
 
        # Result panel below code view
        self.result_view = scrolledtext.ScrolledText(self.result_frame, wrap="none", height=10, state="disabled", bg="#f0f0f0")
        ##self.result_view = scrolledtext.ScrolledText(self.root, height=10, wrap="none", bg="#f0f0f0", state="disabled")
        self.result_view.pack(fill="both", expand=True)
        self.result_view.config(font=(self.font_family, self.font_size))
        self.result_view.bind("<Button-1>", self.on_result_click)
        
        # Add panes with initial layout (bottom)
        self.update_paned_layout()
 
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
 
        #File menu
        filemenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Browse File", command=self.browse_file)
        filemenu.add_command(label="Browse Folder", command=self.browse_folder)
        filemenu.add_command(label="Load", command=self.on_enter_path)
        filemenu.add_separator()
        filemenu.add_command(label="Save Current File", command=self.save_current_file)
        filemenu.add_command(label="Save All Files", command=self.save_all_files)
        filemenu.add_separator()
        filemenu.add_command(label="Save Results", command=self.save_results)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        
 
        # Edit Menu
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
        editmenu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
        editmenu.add_separator()
        editmenu.add_command(label="Cut", accelerator="Ctrl+X", command=self.cut)
        editmenu.add_command(label="Copy", accelerator="Ctrl+C", command=self.copy)
        editmenu.add_command(label="Paste", accelerator="Ctrl+V", command=self.paste)
        editmenu.add_command(label="Select All", accelerator="Ctrl+A", command=self.select_all)
        menubar.add_cascade(label="Edit", menu=editmenu)
 
        # View Menu
        viewmenu = tk.Menu(menubar, tearoff=0)
        fontmenu = tk.Menu(viewmenu, tearoff=0)
 
        # Font families (common ones)
        for fam in ["Courier", "Consolas", "Arial", "Times New Roman", "Helvetica"]:
            fontmenu.add_command(label=fam, command=lambda f=fam: self.set_font_family(f))
        viewmenu.add_cascade(label="Font Family", menu=fontmenu)
 
        # Font size submenu
        sizemenu = tk.Menu(viewmenu, tearoff=0)
        for size in range(8, 20, 2):
            sizemenu.add_command(label=str(size), command=lambda s=size: self.set_font_size(s))
        viewmenu.add_cascade(label="Font Size", menu=sizemenu)
 
        # Theme submenu
        thememenu = tk.Menu(viewmenu, tearoff=0)
        thememenu.add_command(label="Light", command=lambda: self.set_theme("light"))
        thememenu.add_command(label="Dark", command=lambda: self.set_theme("dark"))
        viewmenu.add_cascade(label="Theme", menu=thememenu)
 
        # Result Panel position
        viewmenu.add_separator()
        viewmenu.add_command(label="Toggle Result Panel Position", command=self.toggle_result_position, accelerator="Ctrl+T")
 
        menubar.add_cascade(label="View", menu=viewmenu)
 
    def apply_theme(self):
        if self.theme == "light":
            bg = "white"
            fg = "black"
            comment_fg = "gray"
            keyword_fg = "blue"
            uvm_fg = "darkgreen"
            string_fg = "brown"
            highlight_bg = "yellow"
            highlight_fg = "#000000"   # black text color for visibility on yellow
            search_bg = "lightblue"
            result_bg = "#f0f0f0"
            result_fg = "black"
        else:
            bg = "#1e1e1e"
            fg = "white"
            comment_fg = "#888888"
            keyword_fg = "#569CD6"
            uvm_fg = "#6A9955"
            string_fg = "#D69D85"
            highlight_bg = "#ffff00"
            highlight_fg = "#000000"   # black text color for visibility on yellow
            search_bg = "#264F78"
            result_bg = "#252526"
            result_fg = "white"
 
        self.code_view.config(bg=bg, fg=fg, insertbackground=fg,
                             font=(self.font_family, self.font_size))
        self.result_view.config(bg=result_bg, fg=result_fg, insertbackground=result_fg,
                                font=(self.font_family, self.font_size))
 
        self.code_view.tag_config("keyword", foreground=keyword_fg,
                                 font=(self.font_family, self.font_size, "bold"))
        self.code_view.tag_config("uvm", foreground=uvm_fg,
                                 font=(self.font_family, self.font_size, "bold"))
        self.code_view.tag_config("comment", foreground=comment_fg,
                                 font=(self.font_family, self.font_size, "italic"))
        self.code_view.tag_config("string", foreground=string_fg)
        ##self.code_view.tag_config("highlight", background=highlight_bg)
        self.code_view.tag_config("highlight", background=highlight_bg, foreground=highlight_fg)
        self.code_view.tag_config("search", background=search_bg)
 
    def set_font_family(self, family):
        self.font_family = family
        self.apply_theme()
 
    def set_font_size(self, size):
        self.font_size = size
        self.apply_theme()
 
    def set_theme(self, theme):
        self.theme = theme
        self.apply_theme()
 
    def bind_shortcuts(self):
        self.code_view.bind("<Control-f>", lambda e: self.focus_search())
        self.code_view.bind("<Control-z>", lambda e: self.undo())
        self.code_view.bind("<Control-y>", lambda e: self.redo())
        self.code_view.bind("<Control-a>", lambda e: self.select_all())
        self.code_view.bind("<Control-c>", lambda e: self.copy())
        self.code_view.bind("<Control-x>", lambda e: self.cut())
        self.code_view.bind("<Control-v>", lambda e: self.paste())
 
        self.root.bind_all("<Control-t>", lambda e: self.toggle_result_position())
 
    def update_paned_layout(self):
        # Clear all panes
        for pane in self.paned.panes():
            self.paned.forget(pane)
 
        pos = self.result_positions[self.result_pos_idx]
 
        if pos == "bottom":
            self.paned.config(orient=tk.VERTICAL)
            self.paned.add(self.code_frame)
            self.paned.add(self.result_frame)
        elif pos == "top":
            self.paned.config(orient=tk.VERTICAL)
            self.paned.add(self.result_frame)
            self.paned.add(self.code_frame)
        elif pos == "right":
            self.paned.config(orient=tk.HORIZONTAL)
            self.paned.add(self.code_frame)
            self.paned.add(self.result_frame)
        elif pos == "left":
            self.paned.config(orient=tk.HORIZONTAL)
            self.paned.add(self.result_frame)
            self.paned.add(self.code_frame)
 
    def toggle_result_position(self):
        self.result_pos_idx = (self.result_pos_idx + 1) % len(self.result_positions)
        self.update_paned_layout()
 
 
 
 
    def undo(self):
        try:
            self.code_view.edit_undo()
        except tk.TclError:
            pass
 
    def redo(self):
        try:
            self.code_view.edit_redo()
        except tk.TclError:
            pass
 
    def copy(self):
        try:
            self.code_view.event_generate("<<Copy>>")
        except:
            pass
 
    def cut(self):
        try:
            self.code_view.event_generate("<<Cut>>")
        except:
            pass
 
    def paste(self):
        try:
            self.code_view.event_generate("<<Paste>>")
        except:
            pass
 
    def select_all(self):
        self.code_view.tag_add("sel", "1.0", tk.END)
        return "break"
 
    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("SV files", "*.sv"), ("All files", "*.*")])
        if path:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, path)
 
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, folder)
 
    def on_enter_path(self, event=None):
        self.load_path()
 
    def load_path(self):
        path = self.entry_path.get().strip()
        if os.path.isfile(path):
            self.load_single_file_async(path)
        elif os.path.isdir(path):
            self.load_folder_async(path)
        else:
            messagebox.showerror("Error", f"Invalid path: {path}")
 
    def load_single_file_async(self, filepath):
        self.current_file = filepath
        self.file_line_offsets = []
        self.lines = []
        self.loaded_lines = 0
        self.code_view.config(state="normal")
        self.code_view.delete("1.0", tk.END)
 
        def worker():
            try:
                with open(filepath, "r", errors="ignore") as f:
                    all_lines = f.readlines()
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Cannot open file: {e}"))
                return
 
            self.file_line_offsets = [(filepath, 0, len(all_lines))]
            self.lines = all_lines
            self.root.after(0, self.load_initial_chunk)
 
        threading.Thread(target=worker, daemon=True).start()
def load_initial_chunk(self):
        self.code_view.config(state="normal")
        self.code_view.delete("1.0", tk.END)
        self.loaded_lines = 0
        self.load_more_lines()
 
    def load_more_lines(self):
        end = min(len(self.lines), self.loaded_lines + self.chunk_size)
        chunk = self.lines[self.loaded_lines:end]
        if not chunk:
            return
        # Insert chunk with line numbers
        insert_text = "".join(f"{i+1:5}: {line}" for i, line in enumerate(chunk, start=self.loaded_lines))
        self.code_view.insert(tk.END, insert_text)
        self.loaded_lines = end
        self.highlight_syntax_range(self.loaded_lines - len(chunk) + 1, self.loaded_lines)
 
    # --------------- Save current/all files ---------------
 
    def save_current_file(self):
        if not self.current_file:
            messagebox.showinfo("Save", "No single file loaded to save.")
            return
        try:
            content = self.code_view.get("1.0", tk.END)
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Save", f"Saved file: {self.current_file}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))
 
    def save_all_files(self):
        # For multi-file folder load, we can save all files separately
        if self.current_file:
            self.save_current_file()
            return
 
        if not self.file_line_offsets or not self.lines:
            messagebox.showinfo("Save All", "No files loaded to save.")
            return
 
        try:
            for (fname, start, count) in self.file_line_offsets:
                content = "".join(self.lines[start : start + count])
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(content)
            messagebox.showinfo("Save All", "All files saved successfully.")
        except Exception as e:
            messagebox.showerror("Save All Error", str(e))
 
    def highlight_syntax_range(self, start_line, end_line):
        # Only highlight the visible chunk to save time
        start_index = f"{start_line}.0"
        end_index = f"{end_line}.end"
 
        text = self.code_view.get(start_index, end_index)
 
        # Remove old tags in range
        for tag in ("keyword", "uvm", "comment", "string"):
            self.code_view.tag_remove(tag, start_index, end_index)
 
        # Strings
        for m in re.finditer(r'"(?:\\.|[^"\\])*"', text):
            s = f"{start_line}.0 + {m.start()}c"
            e = f"{start_line}.0 + {m.end()}c"
            self.code_view.tag_add("string", s, e)
 
        # Single-line comments
        for m in re.finditer(r"//.*", text):
            s = f"{start_line}.0 + {m.start()}c"
            e = f"{start_line}.0 + {m.end()}c"
            self.code_view.tag_add("comment", s, e)
 
        # Multi-line comments (simple version)
        multi_comment_pat = re.compile(r"/\*.*?\*/", re.DOTALL)
        for m in multi_comment_pat.finditer(text):
            s = f"{start_line}.0 + {m.start()}c"
            e = f"{start_line}.0 + {m.end()}c"
            self.code_view.tag_add("comment", s, e)
 
        for m in self.pattern_sv.finditer(text):
            s = f"{start_line}.0 + {m.start()}c"
            e = f"{start_line}.0 + {m.end()}c"
            self.code_view.tag_add("keyword", s, e)
 
        for m in self.pattern_uvm.finditer(text):
            s = f"{start_line}.0 + {m.start()}c"
            e = f"{start_line}.0 + {m.end()}c"
            self.code_view.tag_add("uvm", s, e)
 
    def save_results(self):
        if not self.result_map:
            messagebox.showinfo("Save Results", "No results to save.")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    for line in self.result_map:
                        f.write(line + "\n")
                messagebox.showinfo("Save Results", f"Results saved to {filename}")
            except Exception as e:
                messagebox.showerror("Save Results Error", str(e))
 
    def on_scroll(self, event):
        # Detect if near bottom, load more lines
        last_visible_line = int(self.code_view.index("@0,%d" % self.code_view.winfo_height()).split('.')[0])
        if self.loaded_lines - last_visible_line < 50:
            self.load_more_lines()
 
    def on_key_release(self, event):
        # Re-highlight current visible lines on key release
        first_line = int(self.code_view.index("@0,0").split('.')[0])
        last_line = int(self.code_view.index(f"@0,{self.code_view.winfo_height()}").split('.')[0])
        self.highlight_syntax_range(first_line, min(last_line, self.loaded_lines))
 
    def on_code_click(self, event):
        try:
            idx = self.code_view.index(f"@{event.x},{event.y}")
            word = self.code_view.get(f"{idx} wordstart", f"{idx} wordend").strip()
            if word:
                self.analyze_variable(word)
        except Exception as e:
            print("on_code_click error:", e)
 
    def analyze_variable(self, varname):
        readers = []
        writers = []
        self.result_map.clear()
        pat = re.compile(rf"\b{re.escape(varname)}\b")
        assign_pat = re.compile(rf"\b{re.escape(varname)}\b\s*(=|<=)")
 
        for (fname, off, cnt) in self.file_line_offsets:
            for i in range(cnt):
                gi = off + i
                line = self.lines[gi].rstrip("\n")
                if pat.search(line):
                    key = f"{os.path.basename(fname)}:{i+1}: {line}"
                    if assign_pat.search(line):
                        writers.append(key)
                    else:
                        readers.append(key)
                    self.result_map[key] = (fname, i + 1)
 
        self.result_view.config(state="normal")
        self.result_view.delete("1.0", tk.END)
        self.result_view.insert(tk.END, f" Readers of '{varname}':\n")
        for r in readers:
            self.result_view.insert(tk.END, r + "\n")
        self.result_view.insert(tk.END, f"\n✍️ Writers of '{varname}':\n")
        for w in writers:
            self.result_view.insert(tk.END, w + "\n")
        self.result_view.config(state="disabled")
 
    def on_result_click(self, event):
        idx = self.result_view.index(f"@{event.x},{event.y}")
        text = self.result_view.get(f"{idx} linestart", f"{idx} lineend").strip()
        if text in self.result_map:
            fname, ln = self.result_map[text]
            if self.current_file != fname:
                # Load selected file (switch)
                self.load_single_file_async(fname)
                self.root.after(1000, lambda: self.highlight_line(ln))  # delay highlight to after load
            else:
                self.highlight_line(ln)
 
    def highlight_line(self, ln):
        self.code_view.tag_remove("highlight", "1.0", tk.END)
        start = f"{ln}.0"
        end = f"{ln}.end"
        self.code_view.tag_add("highlight", start, end)
        self.code_view.see(start)
 
def main():
    root = tk.Tk()
    app = SVUVMAnalyzerFast(root)
    root.mainloop()
 
if __name__ == "__main__":
    main()

 

