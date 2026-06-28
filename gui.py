"""
gui.py - Main GUI for Resume Builder System
Tabs: Personal | Experience | Education | Projects | Skills | Certifications | Settings
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading, time, os
from pathlib import Path

from models import Resume, Education, Skill, Certification, Project, Experience
from file_manager import FileManager
from resume_generator import ResumeGenerator

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ---------------------------------------------------------------------------
# Themes
# ---------------------------------------------------------------------------
THEMES = {
    "light": {
        "bg":"#f0f2f5","fg":"#2c3e50","panel":"#ffffff",
        "accent":"#2980b9","accent_fg":"#ffffff",
        "entry_bg":"#ffffff","entry_fg":"#2c3e50",
        "list_bg":"#f8f9fa","border":"#dce1e7",
        "header_bg":"#2c3e50","header_fg":"#ffffff",
        "btn":"#2980b9","btn_fg":"#ffffff",
        "btn2":"#27ae60","btn3":"#e74c3c","btn4":"#8e44ad",
        "tab_bg":"#dce1e7",
    },
    "dark": {
        "bg":"#1e1e2e","fg":"#cdd6f4","panel":"#313244",
        "accent":"#89b4fa","accent_fg":"#1e1e2e",
        "entry_bg":"#45475a","entry_fg":"#cdd6f4",
        "list_bg":"#181825","border":"#45475a",
        "header_bg":"#181825","header_fg":"#cdd6f4",
        "btn":"#89b4fa","btn_fg":"#1e1e2e",
        "btn2":"#a6e3a1","btn3":"#f38ba8","btn4":"#cba6f7",
        "tab_bg":"#181825",
    },
}


# ===========================================================================
class ResumeApp(tk.Tk):
    # -----------------------------------------------------------------------
    def __init__(self):
        super().__init__()
        self.title("Resume Builder System")
        self.geometry("1220x780")
        self.minsize(960, 640)

        self.resume        = Resume()
        self.fm            = FileManager()
        self.current_theme = "light"
        self._auto_save_running = False
        self._photo_image  = None

        self._apply_theme()
        self._build_menu()
        self._build_toolbar()
        self._build_main()
        self._start_auto_save()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # =======================================================================
    # Theme helpers
    # =======================================================================
    def _T(self): return THEMES[self.current_theme]

    def _apply_theme(self):
        T = self._T()
        self.configure(bg=T["bg"])
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".",               background=T["bg"],     foreground=T["fg"],     font=("Segoe UI",10))
        s.configure("TFrame",          background=T["bg"])
        s.configure("Card.TFrame",     background=T["panel"])
        s.configure("TLabel",          background=T["bg"],     foreground=T["fg"])
        s.configure("Card.TLabel",     background=T["panel"],  foreground=T["fg"])
        s.configure("Section.TLabel",  background=T["panel"],  foreground=T["accent"], font=("Segoe UI",11,"bold"))
        s.configure("TEntry",          fieldbackground=T["entry_bg"], foreground=T["entry_fg"], insertcolor=T["entry_fg"])
        s.configure("TCombobox",       fieldbackground=T["entry_bg"], foreground=T["entry_fg"])
        s.configure("TNotebook",       background=T["tab_bg"])
        s.configure("TNotebook.Tab",   background=T["tab_bg"], foreground=T["fg"],     padding=(10,5))
        s.map("TNotebook.Tab",         background=[("selected",T["panel"])],
                                       foreground=[("selected",T["accent"])])
        s.configure("Treeview",        background=T["list_bg"],foreground=T["fg"],
                                       fieldbackground=T["list_bg"], rowheight=26)
        s.configure("Treeview.Heading",background=T["accent"], foreground=T["accent_fg"],
                                       font=("Segoe UI",9,"bold"))
        s.map("Treeview",              background=[("selected",T["accent"])],
                                       foreground=[("selected",T["accent_fg"])])

        self._btn_cfg  = dict(bg=T["btn"],  fg=T["btn_fg"],  relief="flat", cursor="hand2", padx=10, pady=4, bd=0,
                              activebackground=T["accent"], activeforeground=T["accent_fg"])
        self._btn2_cfg = dict(bg=T["btn2"], fg="#ffffff",    relief="flat", cursor="hand2", padx=10, pady=4, bd=0,
                              activebackground=T["btn2"])
        self._btn3_cfg = dict(bg=T["btn3"], fg="#ffffff",    relief="flat", cursor="hand2", padx=10, pady=4, bd=0,
                              activebackground=T["btn3"])
        self._btn4_cfg = dict(bg=T["btn4"], fg=T["btn_fg"],  relief="flat", cursor="hand2", padx=10, pady=4, bd=0,
                              activebackground=T["btn4"])

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self._apply_theme()
        for w in self.winfo_children(): w.destroy()
        self._build_menu(); self._build_toolbar(); self._build_main(); self._start_auto_save()

    # =======================================================================
    # Menu
    # =======================================================================
    def _build_menu(self):
        T = self._T()
        mb = tk.Menu(self, bg=T["panel"], fg=T["fg"], tearoff=0)
        fm = tk.Menu(mb, tearoff=0, bg=T["panel"], fg=T["fg"])
        fm.add_command(label="New Resume",       command=self.clear_form)
        fm.add_command(label="Save Data (JSON)", command=self.save_data)
        fm.add_command(label="Load Data…",       command=self._open_load_dialog)
        fm.add_separator()
        fm.add_command(label="Export TXT",       command=self.export_txt)
        fm.add_command(label="Export PDF",       command=self.export_pdf)
        fm.add_separator()
        fm.add_command(label="Exit",             command=self._on_close)
        mb.add_cascade(label="File", menu=fm)
        vm = tk.Menu(mb, tearoff=0, bg=T["panel"], fg=T["fg"])
        vm.add_command(label="Toggle Dark/Light Mode", command=self.toggle_theme)
        mb.add_cascade(label="View", menu=vm)
        hm = tk.Menu(mb, tearoff=0, bg=T["panel"], fg=T["fg"])
        hm.add_command(label="About", command=self._show_about)
        mb.add_cascade(label="Help", menu=hm)
        self.config(menu=mb)

    # =======================================================================
    # Toolbar
    # =======================================================================
    def _build_toolbar(self):
        T = self._T()
        bar = tk.Frame(self, bg=T["header_bg"], pady=4)
        bar.pack(fill="x")
        tk.Label(bar, text="  📄 Resume Builder System",
                 bg=T["header_bg"], fg=T["header_fg"],
                 font=("Segoe UI",14,"bold")).pack(side="left", padx=10)
        for lbl, cmd, cfg in reversed([
            ("🌓 Theme",      self.toggle_theme,        self._btn4_cfg),
            ("💾 Save",       self.save_data,           self._btn_cfg),
            ("📂 Load",       self._open_load_dialog,   self._btn_cfg),
            ("👁 Preview",    self.generate_preview,    self._btn2_cfg),
            ("📤 Export TXT", self.export_txt,          self._btn2_cfg),
            ("📄 Export PDF", self.export_pdf,          self._btn2_cfg),
            ("🗑 Clear",      self.clear_form,          self._btn3_cfg),
        ]):
            tk.Button(bar, text=lbl, command=cmd, **cfg).pack(side="right", padx=4)

    # =======================================================================
    # Main layout
    # =======================================================================
    def _build_main(self):
        T = self._T()
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=8, pady=8)

        left = ttk.Frame(paned, style="Card.TFrame")
        paned.add(left, weight=3)
        nb = ttk.Notebook(left)
        nb.pack(fill="both", expand=True, padx=4, pady=4)

        self._build_personal_tab(nb)
        self._build_experience_tab(nb)
        self._build_education_tab(nb)
        self._build_projects_tab(nb)
        self._build_skills_tab(nb)
        self._build_certifications_tab(nb)
        self._build_settings_tab(nb)

        right = ttk.Frame(paned, style="Card.TFrame")
        paned.add(right, weight=2)
        ttk.Label(right, text="Resume Preview", style="Section.TLabel").pack(anchor="w", padx=10, pady=(10,4))
        self.preview_text = scrolledtext.ScrolledText(
            right, wrap="word", font=("Courier New",9),
            bg=T["list_bg"], fg=T["fg"], insertbackground=T["fg"], relief="flat", bd=0)
        self.preview_text.pack(fill="both", expand=True, padx=6, pady=(0,6))

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self, textvariable=self.status_var, bg=T["header_bg"], fg=T["header_fg"],
                 anchor="w", padx=10, font=("Segoe UI",9)).pack(fill="x", side="bottom")

    # =======================================================================
    # Helper: scrollable card frame
    # =======================================================================
    def _scrollable(self, parent):
        """Returns (canvas, inner_frame) with vertical scrollbar."""
        T = self._T()
        canvas = tk.Canvas(parent, bg=T["panel"], highlightthickness=0)
        sb     = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        inner  = ttk.Frame(canvas, style="Card.TFrame")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        # Mouse-wheel scrolling
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        return inner

    # =======================================================================
    # Tab: Personal
    # =======================================================================
    def _build_personal_tab(self, nb):
        T = self._T()
        frame = ttk.Frame(nb, style="Card.TFrame")
        nb.add(frame, text="  👤 Personal  ")
        inner = self._scrollable(frame)

        ttk.Label(inner, text="Personal Information",
                  style="Section.TLabel").grid(row=0, column=0, columnspan=3,
                                               sticky="w", padx=12, pady=(12,6))

        # Photo thumbnail (right column)
        self.photo_label = tk.Label(inner, text="No Photo\n(click to add)",
                                    bg=T["entry_bg"], fg=T["fg"],
                                    width=14, height=7, cursor="hand2", relief="groove")
        self.photo_label.grid(row=1, column=2, rowspan=5, padx=12, pady=4, sticky="n")
        self.photo_label.bind("<Button-1>", lambda e: self._pick_photo())

        fields = [("Full Name *","name"),("Email *","email"),("Phone","phone"),
                  ("Address","address"),("LinkedIn","linkedin"),("GitHub","github")]
        self._personal_vars = {}
        for i,(lbl,key) in enumerate(fields):
            ttk.Label(inner, text=lbl, style="Card.TLabel"
                      ).grid(row=i+1, column=0, sticky="e", padx=(12,6), pady=5)
            var = tk.StringVar(); self._personal_vars[key] = var
            ttk.Entry(inner, textvariable=var, width=36
                      ).grid(row=i+1, column=1, sticky="ew", pady=5)

        r = len(fields)+1
        ttk.Label(inner, text="Career Objective", style="Card.TLabel"
                  ).grid(row=r, column=0, sticky="ne", padx=(12,6), pady=5)
        self.objective_text = tk.Text(inner, height=5, width=36,
                                      bg=T["entry_bg"], fg=T["entry_fg"],
                                      insertbackground=T["entry_fg"],
                                      relief="flat", bd=1, font=("Segoe UI",10))
        self.objective_text.grid(row=r, column=1, sticky="ew", pady=5, padx=(0,12))
        inner.columnconfigure(1, weight=1)

    def _pick_photo(self):
        path = filedialog.askopenfilename(
            title="Select Profile Photo",
            filetypes=[("Images","*.png *.jpg *.jpeg *.gif *.bmp"),("All","*.*")])
        if not path: return
        self.resume.person.photo_path = path
        if PIL_AVAILABLE:
            try:
                img = Image.open(path).resize((100,110), Image.LANCZOS)
                self._photo_image = ImageTk.PhotoImage(img)
                self.photo_label.config(image=self._photo_image, text="")
            except Exception:
                self.photo_label.config(text="Photo set")
        else:
            self.photo_label.config(text="Photo set\n(PIL missing)")

    # =======================================================================
    # Tab: Experience  (NEW)
    # =======================================================================
    def _build_experience_tab(self, nb):
        T = self._T()
        frame = ttk.Frame(nb, style="Card.TFrame")
        nb.add(frame, text="  💼 Experience  ")

        ttk.Label(frame, text="Work / Internship Experience",
                  style="Section.TLabel").pack(anchor="w", padx=12, pady=(10,4))

        # ---- Entry form ----------------------------------------------------
        ef = ttk.Frame(frame, style="Card.TFrame")
        ef.pack(fill="x", padx=12, pady=4)

        exp_fields = [
            ("Job Title *",  "exp_title"),
            ("Company *",    "exp_company"),
            ("Location",     "exp_location"),
            ("Start Date",   "exp_start"),
            ("End Date",     "exp_end"),
        ]
        self._exp_vars = {}
        for i,(lbl,key) in enumerate(exp_fields):
            ttk.Label(ef, text=lbl, style="Card.TLabel"
                      ).grid(row=i, column=0, sticky="e", padx=(0,6), pady=3)
            var = tk.StringVar(); self._exp_vars[key] = var
            ttk.Entry(ef, textvariable=var, width=40
                      ).grid(row=i, column=1, sticky="ew", pady=3)

        # Multi-line description
        ttk.Label(ef, text="Description\n(one bullet\nper line)",
                  style="Card.TLabel").grid(row=len(exp_fields), column=0,
                                            sticky="ne", padx=(0,6), pady=3)
        self.exp_desc = tk.Text(ef, height=4, width=40,
                                bg=T["entry_bg"], fg=T["entry_fg"],
                                insertbackground=T["entry_fg"],
                                relief="flat", bd=1, font=("Segoe UI",10))
        self.exp_desc.grid(row=len(exp_fields), column=1, sticky="ew", pady=3)
        ef.columnconfigure(1, weight=1)

        # ---- Buttons -------------------------------------------------------
        bf = ttk.Frame(frame, style="Card.TFrame")
        bf.pack(fill="x", padx=12, pady=6)
        tk.Button(bf, text="➕ Add Experience",    command=self._add_exp,    **self._btn2_cfg).pack(side="left", padx=4)
        tk.Button(bf, text="✏️ Update Selected",   command=self._update_exp, **self._btn_cfg).pack(side="left", padx=4)
        tk.Button(bf, text="🗑 Remove Selected",   command=self._remove_exp, **self._btn3_cfg).pack(side="left", padx=4)

        # ---- Treeview ------------------------------------------------------
        cols = ("title","company","location","period")
        self.exp_tree = ttk.Treeview(frame, columns=cols, show="headings", height=7)
        for c,w,h in zip(cols,[160,150,100,140],
                         ["Job Title","Company","Location","Period"]):
            self.exp_tree.heading(c, text=h)
            self.exp_tree.column(c, width=w, anchor="w")
        self.exp_tree.pack(fill="both", expand=True, padx=12, pady=(0,10))
        self.exp_tree.bind("<ButtonRelease-1>", self._exp_row_click)

    def _add_exp(self):
        title   = self._exp_vars["exp_title"].get().strip()
        company = self._exp_vars["exp_company"].get().strip()
        if not title or not company:
            messagebox.showwarning("Missing Fields","Job Title and Company are required.")
            return
        loc   = self._exp_vars["exp_location"].get().strip()
        start = self._exp_vars["exp_start"].get().strip()
        end   = self._exp_vars["exp_end"].get().strip()
        desc  = self.exp_desc.get("1.0","end").strip()
        exp = Experience()
        exp.add_experience(title, company, loc, start, end, desc)
        self.resume.experiences.append(exp)
        period = f"{start} – {end}" if start else ""
        self.exp_tree.insert("","end", values=(title, company, loc, period))
        self._clear_exp_form()
        self._set_status("Experience added.")

    def _update_exp(self):
        sel = self.exp_tree.selection()
        if not sel:
            messagebox.showinfo("No Selection","Select a row to update.")
            return
        idx = self.exp_tree.index(sel[0])
        title   = self._exp_vars["exp_title"].get().strip()
        company = self._exp_vars["exp_company"].get().strip()
        if not title or not company:
            messagebox.showwarning("Missing Fields","Job Title and Company are required.")
            return
        loc   = self._exp_vars["exp_location"].get().strip()
        start = self._exp_vars["exp_start"].get().strip()
        end   = self._exp_vars["exp_end"].get().strip()
        desc  = self.exp_desc.get("1.0","end").strip()
        self.resume.experiences[idx].add_experience(title, company, loc, start, end, desc)
        period = f"{start} – {end}" if start else ""
        self.exp_tree.item(sel[0], values=(title, company, loc, period))
        self._clear_exp_form()
        self._set_status("Experience updated.")

    def _remove_exp(self):
        sel = self.exp_tree.selection()
        if not sel:
            messagebox.showinfo("No Selection","Select a row to remove.")
            return
        idx = self.exp_tree.index(sel[0])
        self.exp_tree.delete(sel[0])
        del self.resume.experiences[idx]
        self._set_status("Experience removed.")

    def _exp_row_click(self, _=None):
        sel = self.exp_tree.selection()
        if not sel: return
        idx = self.exp_tree.index(sel[0])
        exp = self.resume.experiences[idx]
        self._exp_vars["exp_title"].set(exp.job_title)
        self._exp_vars["exp_company"].set(exp.company)
        self._exp_vars["exp_location"].set(exp.location)
        self._exp_vars["exp_start"].set(exp.start_date)
        self._exp_vars["exp_end"].set(exp.end_date)
        self.exp_desc.delete("1.0","end")
        self.exp_desc.insert("1.0", exp.description)

    def _clear_exp_form(self):
        for v in self._exp_vars.values(): v.set("")
        self.exp_desc.delete("1.0","end")

    # =======================================================================
    # Tab: Education
    # =======================================================================
    def _build_education_tab(self, nb):
        T = self._T()
        frame = ttk.Frame(nb, style="Card.TFrame")
        nb.add(frame, text="  🎓 Education  ")

        ttk.Label(frame, text="Education Records",
                  style="Section.TLabel").pack(anchor="w", padx=12, pady=(10,4))

        ef = ttk.Frame(frame, style="Card.TFrame")
        ef.pack(fill="x", padx=12)
        self._edu_vars = {}
        for i,(lbl,key) in enumerate([("Degree","edu_degree"),("Institution","edu_inst"),
                                       ("Passing Year","edu_year"),("CGPA/Score","edu_cgpa")]):
            ttk.Label(ef, text=lbl, style="Card.TLabel"
                      ).grid(row=i, column=0, sticky="e", padx=(0,6), pady=4)
            var = tk.StringVar(); self._edu_vars[key] = var
            ttk.Entry(ef, textvariable=var, width=38
                      ).grid(row=i, column=1, sticky="ew", pady=4)
        ef.columnconfigure(1, weight=1)

        bf = ttk.Frame(frame, style="Card.TFrame")
        bf.pack(fill="x", padx=12, pady=6)
        tk.Button(bf, text="➕ Add Education",  command=self._add_edu,  **self._btn2_cfg).pack(side="left", padx=4)
        tk.Button(bf, text="🗑 Remove Selected", command=self._remove_edu, **self._btn3_cfg).pack(side="left", padx=4)

        cols = ("degree","institution","year","cgpa")
        self.edu_tree = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        for c,w,h in zip(cols,[150,200,80,80],["Degree","Institution","Year","CGPA"]):
            self.edu_tree.heading(c,text=h); self.edu_tree.column(c,width=w,anchor="w")
        self.edu_tree.pack(fill="both", expand=True, padx=12, pady=(0,10))
        self.edu_tree.bind("<ButtonRelease-1>", self._edu_row_click)

    def _add_edu(self):
        d,i,y,c = (self._edu_vars[k].get().strip()
                   for k in ["edu_degree","edu_inst","edu_year","edu_cgpa"])
        if not d or not i:
            messagebox.showwarning("Missing","Degree and Institution are required.")
            return
        edu = Education(); edu.add_record(d,i,y,c)
        self.resume.educations.append(edu)
        self.edu_tree.insert("","end",values=(d,i,y,c))
        for v in self._edu_vars.values(): v.set("")
        self._set_status("Education added.")

    def _remove_edu(self):
        sel = self.edu_tree.selection()
        if not sel: messagebox.showinfo("No Selection","Select a row."); return
        idx = self.edu_tree.index(sel[0])
        self.edu_tree.delete(sel[0]); del self.resume.educations[idx]
        self._set_status("Education removed.")

    def _edu_row_click(self, _=None):
        sel = self.edu_tree.selection()
        if not sel: return
        v = self.edu_tree.item(sel[0],"values")
        for k,val in zip(["edu_degree","edu_inst","edu_year","edu_cgpa"], v):
            self._edu_vars[k].set(val)

    # =======================================================================
    # Tab: Projects  (NEW)
    # =======================================================================
    def _build_projects_tab(self, nb):
        T = self._T()
        frame = ttk.Frame(nb, style="Card.TFrame")
        nb.add(frame, text="  🚀 Projects  ")

        ttk.Label(frame, text="Projects",
                  style="Section.TLabel").pack(anchor="w", padx=12, pady=(10,4))

        ef = ttk.Frame(frame, style="Card.TFrame")
        ef.pack(fill="x", padx=12, pady=4)

        proj_fields = [
            ("Title *",    "proj_title"),
            ("Tech Stack", "proj_tech"),
            ("Duration",   "proj_dur"),
            ("Link/URL",   "proj_link"),
        ]
        self._proj_vars = {}
        for i,(lbl,key) in enumerate(proj_fields):
            ttk.Label(ef, text=lbl, style="Card.TLabel"
                      ).grid(row=i, column=0, sticky="e", padx=(0,6), pady=3)
            var = tk.StringVar(); self._proj_vars[key] = var
            ttk.Entry(ef, textvariable=var, width=40
                      ).grid(row=i, column=1, sticky="ew", pady=3)

        ttk.Label(ef, text="Description", style="Card.TLabel"
                  ).grid(row=len(proj_fields), column=0, sticky="ne", padx=(0,6), pady=3)
        self.proj_desc = tk.Text(ef, height=3, width=40,
                                 bg=T["entry_bg"], fg=T["entry_fg"],
                                 insertbackground=T["entry_fg"],
                                 relief="flat", bd=1, font=("Segoe UI",10))
        self.proj_desc.grid(row=len(proj_fields), column=1, sticky="ew", pady=3)
        ef.columnconfigure(1, weight=1)

        bf = ttk.Frame(frame, style="Card.TFrame")
        bf.pack(fill="x", padx=12, pady=6)
        tk.Button(bf, text="➕ Add Project",     command=self._add_proj,    **self._btn2_cfg).pack(side="left", padx=4)
        tk.Button(bf, text="✏️ Update Selected",  command=self._update_proj, **self._btn_cfg).pack(side="left", padx=4)
        tk.Button(bf, text="🗑 Remove Selected",  command=self._remove_proj, **self._btn3_cfg).pack(side="left", padx=4)

        cols = ("title","tech","duration","link")
        self.proj_tree = ttk.Treeview(frame, columns=cols, show="headings", height=7)
        for c,w,h in zip(cols,[160,160,100,160],["Title","Tech Stack","Duration","Link"]):
            self.proj_tree.heading(c,text=h); self.proj_tree.column(c,width=w,anchor="w")
        self.proj_tree.pack(fill="both", expand=True, padx=12, pady=(0,10))
        self.proj_tree.bind("<ButtonRelease-1>", self._proj_row_click)

    def _add_proj(self):
        title = self._proj_vars["proj_title"].get().strip()
        if not title:
            messagebox.showwarning("Missing","Project title is required."); return
        tech = self._proj_vars["proj_tech"].get().strip()
        dur  = self._proj_vars["proj_dur"].get().strip()
        link = self._proj_vars["proj_link"].get().strip()
        desc = self.proj_desc.get("1.0","end").strip()
        p = Project(); p.add_project(title, tech, dur, desc, link)
        self.resume.projects.append(p)
        self.proj_tree.insert("","end", values=(title, tech, dur, link))
        self._clear_proj_form()
        self._set_status("Project added.")

    def _update_proj(self):
        sel = self.proj_tree.selection()
        if not sel: messagebox.showinfo("No Selection","Select a row."); return
        idx = self.proj_tree.index(sel[0])
        title = self._proj_vars["proj_title"].get().strip()
        if not title: messagebox.showwarning("Missing","Title required."); return
        tech = self._proj_vars["proj_tech"].get().strip()
        dur  = self._proj_vars["proj_dur"].get().strip()
        link = self._proj_vars["proj_link"].get().strip()
        desc = self.proj_desc.get("1.0","end").strip()
        self.resume.projects[idx].add_project(title, tech, dur, desc, link)
        self.proj_tree.item(sel[0], values=(title, tech, dur, link))
        self._clear_proj_form()
        self._set_status("Project updated.")

    def _remove_proj(self):
        sel = self.proj_tree.selection()
        if not sel: messagebox.showinfo("No Selection","Select a row."); return
        idx = self.proj_tree.index(sel[0])
        self.proj_tree.delete(sel[0]); del self.resume.projects[idx]
        self._set_status("Project removed.")

    def _proj_row_click(self, _=None):
        sel = self.proj_tree.selection()
        if not sel: return
        idx = self.proj_tree.index(sel[0])
        proj = self.resume.projects[idx]
        self._proj_vars["proj_title"].set(proj.title)
        self._proj_vars["proj_tech"].set(proj.tech_stack)
        self._proj_vars["proj_dur"].set(proj.duration)
        self._proj_vars["proj_link"].set(proj.link)
        self.proj_desc.delete("1.0","end")
        self.proj_desc.insert("1.0", proj.description)

    def _clear_proj_form(self):
        for v in self._proj_vars.values(): v.set("")
        self.proj_desc.delete("1.0","end")

    # =======================================================================
    # Tab: Skills
    # =======================================================================
    def _build_skills_tab(self, nb):
        T = self._T()
        frame = ttk.Frame(nb, style="Card.TFrame")
        nb.add(frame, text="  🛠 Skills  ")
        ttk.Label(frame, text="Technical & Soft Skills",
                  style="Section.TLabel").pack(anchor="w", padx=12, pady=(10,4))

        inp = ttk.Frame(frame, style="Card.TFrame")
        inp.pack(fill="x", padx=12, pady=4)
        ttk.Label(inp, text="Skill:", style="Card.TLabel").pack(side="left")
        self.skill_var = tk.StringVar()
        ttk.Entry(inp, textvariable=self.skill_var, width=32).pack(side="left", padx=8)
        tk.Button(inp, text="➕ Add",    command=self._add_skill,    **self._btn2_cfg).pack(side="left", padx=4)
        tk.Button(inp, text="🗑 Remove", command=self._remove_skill, **self._btn3_cfg).pack(side="left", padx=4)

        self.skills_listbox = tk.Listbox(frame, bg=T["list_bg"], fg=T["fg"],
                                          selectbackground=T["accent"],
                                          selectforeground=T["accent_fg"],
                                          font=("Segoe UI",10), relief="flat", bd=1)
        self.skills_listbox.pack(fill="both", expand=True, padx=12, pady=(4,12))

    def _add_skill(self):
        name = self.skill_var.get().strip()
        if not name: messagebox.showwarning("Empty","Enter a skill name."); return
        s = Skill(); s.add_skill(name)
        self.resume.skills.append(s)
        self.skills_listbox.insert("end", name)
        self.skill_var.set("")
        self._set_status(f"Skill '{name}' added.")

    def _remove_skill(self):
        sel = self.skills_listbox.curselection()
        if not sel: messagebox.showinfo("No Selection","Select a skill."); return
        idx = sel[0]
        self.skills_listbox.delete(idx); del self.resume.skills[idx]
        self._set_status("Skill removed.")

    # =======================================================================
    # Tab: Certifications
    # =======================================================================
    def _build_certifications_tab(self, nb):
        T = self._T()
        frame = ttk.Frame(nb, style="Card.TFrame")
        nb.add(frame, text="  🏆 Certifications  ")
        ttk.Label(frame, text="Certifications",
                  style="Section.TLabel").pack(anchor="w", padx=12, pady=(10,4))

        ef = ttk.Frame(frame, style="Card.TFrame")
        ef.pack(fill="x", padx=12)
        self._cert_vars = {}
        for i,(lbl,key) in enumerate([("Certificate Name","cert_name"),
                                       ("Organization","cert_org"),
                                       ("Completion Year","cert_year")]):
            ttk.Label(ef, text=lbl, style="Card.TLabel"
                      ).grid(row=i, column=0, sticky="e", padx=(0,6), pady=4)
            var = tk.StringVar(); self._cert_vars[key] = var
            ttk.Entry(ef, textvariable=var, width=38
                      ).grid(row=i, column=1, sticky="ew", pady=4)
        ef.columnconfigure(1, weight=1)

        bf = ttk.Frame(frame, style="Card.TFrame")
        bf.pack(fill="x", padx=12, pady=6)
        tk.Button(bf, text="➕ Add Certification", command=self._add_cert,    **self._btn2_cfg).pack(side="left", padx=4)
        tk.Button(bf, text="🗑 Remove Selected",   command=self._remove_cert, **self._btn3_cfg).pack(side="left", padx=4)

        cols = ("name","org","year")
        self.cert_tree = ttk.Treeview(frame, columns=cols, show="headings", height=8)
        for c,w,h in zip(cols,[220,200,80],["Certificate","Organization","Year"]):
            self.cert_tree.heading(c,text=h); self.cert_tree.column(c,width=w,anchor="w")
        self.cert_tree.pack(fill="both", expand=True, padx=12, pady=(0,10))

    def _add_cert(self):
        name = self._cert_vars["cert_name"].get().strip()
        if not name: messagebox.showwarning("Missing","Certificate name required."); return
        org  = self._cert_vars["cert_org"].get().strip()
        year = self._cert_vars["cert_year"].get().strip()
        c = Certification(); c.add_certificate(name, org, year)
        self.resume.certifications.append(c)
        self.cert_tree.insert("","end",values=(name,org,year))
        for v in self._cert_vars.values(): v.set("")
        self._set_status("Certification added.")

    def _remove_cert(self):
        sel = self.cert_tree.selection()
        if not sel: messagebox.showinfo("No Selection","Select a row."); return
        idx = self.cert_tree.index(sel[0])
        self.cert_tree.delete(sel[0]); del self.resume.certifications[idx]
        self._set_status("Certification removed.")

    # =======================================================================
    # Tab: Settings
    # =======================================================================
    def _build_settings_tab(self, nb):
        T = self._T()
        frame = ttk.Frame(nb, style="Card.TFrame")
        nb.add(frame, text="  ⚙ Settings  ")
        ttk.Label(frame, text="Resume Settings",
                  style="Section.TLabel").pack(anchor="w", padx=12, pady=(10,4))

        sf = ttk.Frame(frame, style="Card.TFrame")
        sf.pack(fill="x", padx=16, pady=8)
        ttk.Label(sf, text="Template:", style="Card.TLabel"
                  ).grid(row=0, column=0, sticky="e", padx=(0,8), pady=6)
        self.template_var = tk.StringVar(value="classic")
        ttk.Combobox(sf, textvariable=self.template_var, width=18,
                     values=["classic","modern","minimal"], state="readonly"
                     ).grid(row=0, column=1, sticky="w", pady=6)
        ttk.Label(sf, text="Auto-Save:", style="Card.TLabel"
                  ).grid(row=1, column=0, sticky="e", padx=(0,8), pady=6)
        self.autosave_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(sf, variable=self.autosave_var, text="Every 60 s"
                        ).grid(row=1, column=1, sticky="w", pady=6)

        ttk.Label(frame, text="Saved Resumes",
                  style="Section.TLabel").pack(anchor="w", padx=12, pady=(16,4))
        search_f = ttk.Frame(frame, style="Card.TFrame")
        search_f.pack(fill="x", padx=12, pady=4)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._update_saved_list())
        ttk.Entry(search_f, textvariable=self.search_var, width=26
                  ).pack(side="left", padx=(0,6))
        tk.Button(search_f, text="🔄 Refresh",
                  command=self._update_saved_list, **self._btn_cfg).pack(side="left")

        self.saved_listbox = tk.Listbox(frame, height=8, bg=T["list_bg"], fg=T["fg"],
                                         selectbackground=T["accent"],
                                         selectforeground=T["accent_fg"],
                                         font=("Segoe UI",10), relief="flat", bd=1)
        self.saved_listbox.pack(fill="both", expand=True, padx=12, pady=(4,4))

        br = ttk.Frame(frame, style="Card.TFrame")
        br.pack(fill="x", padx=12, pady=6)
        tk.Button(br, text="📂 Load Selected",   command=self._load_selected,   **self._btn_cfg).pack(side="left", padx=4)
        tk.Button(br, text="🗑 Delete Selected",  command=self._delete_selected, **self._btn3_cfg).pack(side="left", padx=4)
        self._update_saved_list()

    def _update_saved_list(self):
        q = self.search_var.get().lower()
        self.saved_listbox.delete(0,"end")
        for n in FileManager.list_saved():
            if q in n.lower(): self.saved_listbox.insert("end", n)

    def _load_selected(self):
        sel = self.saved_listbox.curselection()
        if not sel: messagebox.showinfo("No Selection","Select a resume."); return
        self._load_resume(self.saved_listbox.get(sel[0]))

    def _delete_selected(self):
        sel = self.saved_listbox.curselection()
        if not sel: return
        fn = self.saved_listbox.get(sel[0])
        if messagebox.askyesno("Confirm", f"Delete '{fn}'?"):
            try:
                FileManager.delete_saved(fn); self._update_saved_list()
                self._set_status(f"Deleted '{fn}'.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    # =======================================================================
    # Core actions
    # =======================================================================
    def _collect_personal(self):
        """Sync GUI fields → model. photo_path is owned by _pick_photo()."""
        try:
            self.resume.person.update_details(
                name      = self._personal_vars["name"].get().strip(),
                email     = self._personal_vars["email"].get().strip(),
                phone     = self._personal_vars["phone"].get().strip(),
                address   = self._personal_vars["address"].get().strip(),
                linkedin  = self._personal_vars["linkedin"].get().strip(),
                github    = self._personal_vars["github"].get().strip(),
                objective = self.objective_text.get("1.0","end").strip(),
            )
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e)); return False
        self.resume.template = self.template_var.get()
        return True

    def generate_preview(self):
        if not self._collect_personal(): return
        try:
            text = ResumeGenerator(self.resume).get_preview_text()
            self.preview_text.config(state="normal")
            self.preview_text.delete("1.0","end")
            self.preview_text.insert("1.0", text)
            self.preview_text.config(state="disabled")
            self._set_status("Preview generated.")
        except ValueError as e:
            messagebox.showerror("Validation", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_data(self):
        if not self._collect_personal(): return
        try:
            path = self.fm.save_data(self.resume)
            self._update_saved_list()
            self._set_status(f"Saved → {path}")
            messagebox.showinfo("Saved", f"Data saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _open_load_dialog(self):
        path = filedialog.askopenfilename(
            title="Load Resume JSON",
            initialdir=str(Path(__file__).parent / "data"),
            filetypes=[("JSON files","*.json"),("All","*.*")])
        if path: self._load_resume(path)

    def _load_resume(self, filename):
        try:
            self.fm.load_data(filename, self.resume)
            self._populate_gui()
            self._set_status(f"Loaded '{filename}'.")
        except Exception as e:
            messagebox.showerror("Load Error", str(e))

    def _populate_gui(self):
        """Push model → all GUI widgets after loading."""
        p = self.resume.person
        for f in ["name","email","phone","address","linkedin","github"]:
            self._personal_vars[f].set(getattr(p, f, ""))
        self.objective_text.delete("1.0","end")
        self.objective_text.insert("1.0", p.objective)

        # Experience
        self.exp_tree.delete(*self.exp_tree.get_children())
        for exp in self.resume.experiences:
            period = f"{exp.start_date} – {exp.end_date}" if exp.start_date else ""
            self.exp_tree.insert("","end", values=(exp.job_title, exp.company, exp.location, period))

        # Education
        self.edu_tree.delete(*self.edu_tree.get_children())
        for edu in self.resume.educations:
            self.edu_tree.insert("","end", values=(edu.degree, edu.institution, edu.passing_year, edu.cgpa))

        # Projects
        self.proj_tree.delete(*self.proj_tree.get_children())
        for proj in self.resume.projects:
            self.proj_tree.insert("","end", values=(proj.title, proj.tech_stack, proj.duration, proj.link))

        # Skills
        self.skills_listbox.delete(0,"end")
        for s in self.resume.skills:
            self.skills_listbox.insert("end", s.skill_name)

        # Certifications
        self.cert_tree.delete(*self.cert_tree.get_children())
        for c in self.resume.certifications:
            self.cert_tree.insert("","end", values=(c.certificate_name, c.organization, c.completion_year))

        self.template_var.set(self.resume.template)

        # Photo
        pp = p.photo_path
        if pp and os.path.isfile(pp):
            if PIL_AVAILABLE:
                try:
                    img = Image.open(pp).resize((100,110), Image.LANCZOS)
                    self._photo_image = ImageTk.PhotoImage(img)
                    self.photo_label.config(image=self._photo_image, text="")
                except Exception:
                    self.photo_label.config(text="Photo set")
            else:
                self.photo_label.config(text="Photo set\n(PIL missing)")
        else:
            self.photo_label.config(image="", text="No Photo\n(click to add)")
            self._photo_image = None

        self.generate_preview()

    def export_txt(self):
        if not self._collect_personal(): return
        path = filedialog.asksaveasfilename(title="Export TXT", defaultextension=".txt",
                                            filetypes=[("Text","*.txt"),("All","*.*")])
        if not path: return
        try:
            ResumeGenerator(self.resume).export_txt(os.path.dirname(path))
            self._set_status(f"Exported TXT → {path}")
            messagebox.showinfo("Exported", f"TXT saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def export_pdf(self):
        if not self._collect_personal(): return
        path = filedialog.asksaveasfilename(title="Export PDF", defaultextension=".pdf",
                                            filetypes=[("PDF","*.pdf"),("All","*.*")])
        if not path: return
        try:
            out = ResumeGenerator(self.resume).export_pdf(os.path.dirname(path))
            self._set_status(f"Exported PDF → {out}")
            messagebox.showinfo("Exported", f"PDF saved to:\n{out}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def clear_form(self):
        if not messagebox.askyesno("Confirm","Clear all data and start fresh?"): return
        self.resume = Resume()
        for v in self._personal_vars.values(): v.set("")
        self.objective_text.delete("1.0","end")
        self.exp_tree.delete(*self.exp_tree.get_children())
        self.edu_tree.delete(*self.edu_tree.get_children())
        self.proj_tree.delete(*self.proj_tree.get_children())
        self.skills_listbox.delete(0,"end")
        self.cert_tree.delete(*self.cert_tree.get_children())
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0","end")
        self.preview_text.config(state="disabled")
        self._photo_image = None
        self.photo_label.config(image="", text="No Photo\n(click to add)")
        self._set_status("Form cleared.")

    # =======================================================================
    # Auto-save
    # =======================================================================
    def _start_auto_save(self):
        self._auto_save_running = True
        def _loop():
            while self._auto_save_running:
                time.sleep(60)
                if self.autosave_var.get() and self.resume.person.name:
                    try:
                        self._collect_personal()
                        self.fm.save_data(self.resume)
                        self.after(0, lambda: self._set_status("Auto-saved."))
                    except Exception:
                        pass
        threading.Thread(target=_loop, daemon=True).start()

    # =======================================================================
    # Helpers
    # =======================================================================
    def _set_status(self, msg):  self.status_var.set(f"  {msg}")
    def _on_close(self):         self._auto_save_running = False; self.destroy()
    def _show_about(self):
        messagebox.showinfo("About",
            "Resume Builder System v2.0\n"
            "Python 3.12 + Tkinter + ReportLab\n\n"
            "Sections: Personal, Experience, Education,\n"
            "Projects, Skills, Certifications\n"
            "Exports: TXT & PDF  |  Dark / Light mode")
