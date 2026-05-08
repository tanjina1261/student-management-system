import customtkinter as ctk
from tkinter import ttk, messagebox
import database

# ── theme ──────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DEPARTMENTS = ["CSE", "EEE", "BBA", "Civil", "Textile", "Pharmacy", "Law", "English"]

# ── helpers ────────────────────────────────────────────────────────────────────
def make_entry(parent, placeholder, row, col, colspan=1, width=200):
    e = ctk.CTkEntry(parent, placeholder_text=placeholder,
                     width=width, height=38,
                     corner_radius=8, font=("Segoe UI", 13))
    e.grid(row=row, column=col, columnspan=colspan,
           padx=8, pady=6, sticky="ew")
    return e

# ══════════════════════════════════════════════════════════════════════════════
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Student Management System")
        self.geometry("1100x680")
        self.minsize(900, 600)
        self.resizable(True, True)

        database.create_table()
        self._selected_id = None

        self._build_sidebar()
        self._build_main()
        self._show_tab("dashboard")

    # ── sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=200, corner_radius=0,
                          fg_color=("#1a1a2e", "#1a1a2e"))
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        ctk.CTkLabel(sb, text="📚 SMS", font=("Segoe UI", 22, "bold"),
                     text_color="#7c83fd").pack(pady=(30, 4))
        ctk.CTkLabel(sb, text="Student Portal",
                     font=("Segoe UI", 11), text_color="#888").pack(pady=(0, 30))

        self._nav_btns = {}
        nav_items = [
            ("dashboard", "🏠  Dashboard"),
            ("add",       "➕  Add Student"),
            ("records",   "📋  All Records"),
            ("search",    "🔍  Search"),
        ]
        for key, label in nav_items:
            btn = ctk.CTkButton(
                sb, text=label, width=170, height=42,
                corner_radius=10, anchor="w",
                font=("Segoe UI", 13),
                fg_color="transparent",
                hover_color="#2a2a4a",
                text_color="#cccccc",
                command=lambda k=key: self._show_tab(k)
            )
            btn.pack(pady=3, padx=14)
            self._nav_btns[key] = btn

        ctk.CTkFrame(sb, height=1, fg_color="#333").pack(
            fill="x", padx=14, pady=20)
        ctk.CTkLabel(sb, text="v1.0  •  SQLite",
                     font=("Segoe UI", 10), text_color="#555").pack(side="bottom", pady=16)

    # ── main container ────────────────────────────────────────────────────────
    def _build_main(self):
        self._main = ctk.CTkFrame(self, corner_radius=0, fg_color=("#0f0f1a", "#0f0f1a"))
        self._main.pack(side="left", fill="both", expand=True)

        self._frames = {
            "dashboard": self._build_dashboard(self._main),
            "add":       self._build_add(self._main),
            "records":   self._build_records(self._main),
            "search":    self._build_search(self._main),
        }

    def _show_tab(self, key):
        for k, f in self._frames.items():
            f.pack_forget()
        self._frames[key].pack(fill="both", expand=True, padx=24, pady=24)

        for k, btn in self._nav_btns.items():
            btn.configure(
                fg_color="#2a2a4a" if k == key else "transparent",
                text_color="#ffffff" if k == key else "#cccccc"
            )
        if key == "dashboard":
            self._refresh_dashboard()
        if key == "records":
            self._load_records()

    # ── dashboard ─────────────────────────────────────────────────────────────
    def _build_dashboard(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")

        ctk.CTkLabel(f, text="Dashboard",
                     font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(0, 20))

        self._stat_row = ctk.CTkFrame(f, fg_color="transparent")
        self._stat_row.pack(fill="x", pady=(0, 24))

        self._dept_frame = ctk.CTkScrollableFrame(
            f, label_text="Students by Department",
            label_font=("Segoe UI", 14, "bold"),
            fg_color=("#16213e", "#16213e"), corner_radius=12)
        self._dept_frame.pack(fill="both", expand=True)

        return f

    def _stat_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, fg_color=("#16213e", "#16213e"),
                            corner_radius=12)
        card.pack(side="left", expand=True, fill="both", padx=6, pady=4)
        ctk.CTkLabel(card, text=str(value),
                     font=("Segoe UI", 36, "bold"),
                     text_color=color).pack(pady=(18, 2))
        ctk.CTkLabel(card, text=title,
                     font=("Segoe UI", 12), text_color="#aaa").pack(pady=(0, 18))

    def _refresh_dashboard(self):
        for w in self._stat_row.winfo_children():
            w.destroy()
        for w in self._dept_frame.winfo_children():
            w.destroy()

        total, dept_counts = database.get_stats()
        self._stat_card(self._stat_row, "Total Students", total, "#7c83fd")
        self._stat_card(self._stat_row, "Departments",
                        len(dept_counts), "#4ecdc4")
        self._stat_card(self._stat_row, "System Status", "Online", "#44cf6c")

        colors = ["#7c83fd","#4ecdc4","#ff6b6b","#ffd93d",
                  "#44cf6c","#f7971e","#a8edea","#ee9ca7"]
        for i, (dept, count) in enumerate(dept_counts):
            row = ctk.CTkFrame(self._dept_frame, fg_color="transparent")
            row.pack(fill="x", pady=5, padx=10)
            ctk.CTkLabel(row, text=dept, width=120,
                         font=("Segoe UI", 13), anchor="w").pack(side="left")
            bar_bg = ctk.CTkFrame(row, height=18, corner_radius=9,
                                  fg_color="#2a2a4a")
            bar_bg.pack(side="left", fill="x", expand=True, padx=(0, 10))
            bar_bg.update_idletasks()
            w = max(40, int((count / max(total, 1)) * 300))
            ctk.CTkFrame(bar_bg, width=w, height=18, corner_radius=9,
                         fg_color=colors[i % len(colors)]).place(x=0, y=0)
            ctk.CTkLabel(row, text=str(count),
                         font=("Segoe UI", 13, "bold"),
                         text_color=colors[i % len(colors)]).pack(side="left")

    # ── add student ───────────────────────────────────────────────────────────
    def _build_add(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")

        ctk.CTkLabel(f, text="Add / Edit Student",
                     font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(0, 16))

        form = ctk.CTkFrame(f, fg_color=("#16213e","#16213e"), corner_radius=14)
        form.pack(fill="x")
        form.columnconfigure((0,1), weight=1)

        self._e_name   = make_entry(form, "Full Name",    0, 0, width=260)
        self._e_sid    = make_entry(form, "Student ID",   0, 1, width=260)
        self._e_email  = make_entry(form, "Email",        1, 0, width=260)
        self._e_phone  = make_entry(form, "Phone",        1, 1, width=260)
        self._e_cgpa   = make_entry(form, "CGPA (0–4)",   2, 0, width=260)

        self._dept_var = ctk.StringVar(value="CSE")
        dept_menu = ctk.CTkOptionMenu(form, values=DEPARTMENTS,
                                      variable=self._dept_var,
                                      width=260, height=38,
                                      corner_radius=8,
                                      font=("Segoe UI", 13))
        dept_menu.grid(row=2, column=1, padx=8, pady=6, sticky="ew")

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.grid(row=3, column=0, columnspan=2, pady=14)

        ctk.CTkButton(btn_row, text="💾  Save Student",
                      width=180, height=40, corner_radius=10,
                      font=("Segoe UI", 13, "bold"),
                      fg_color="#7c83fd", hover_color="#5a62e0",
                      command=self._save_student).pack(side="left", padx=8)
        ctk.CTkButton(btn_row, text="🗑  Clear Form",
                      width=140, height=40, corner_radius=10,
                      font=("Segoe UI", 13),
                      fg_color="#2a2a4a", hover_color="#3a3a5a",
                      command=self._clear_form).pack(side="left", padx=8)

        self._form_msg = ctk.CTkLabel(f, text="", font=("Segoe UI", 13))
        self._form_msg.pack(pady=10)
        return f

    def _save_student(self):
        name  = self._e_name.get().strip()
        sid   = self._e_sid.get().strip()
        email = self._e_email.get().strip()
        phone = self._e_phone.get().strip()
        cgpa  = self._e_cgpa.get().strip()
        dept  = self._dept_var.get()

        if not all([name, sid, email, phone, cgpa]):
            self._form_msg.configure(text="⚠ Please fill all fields.", text_color="#ff6b6b")
            return

        if self._selected_id:
            ok, msg = database.update_student(
                self._selected_id, name, sid, dept, email, phone, cgpa)
            self._selected_id = None
        else:
            ok, msg = database.add_student(name, sid, dept, email, phone, cgpa)

        color = "#44cf6c" if ok else "#ff6b6b"
        self._form_msg.configure(text=msg, text_color=color)
        if ok:
            self._clear_form()

    def _clear_form(self):
        for e in [self._e_name, self._e_sid, self._e_email,
                  self._e_phone, self._e_cgpa]:
            e.delete(0, "end")
        self._dept_var.set("CSE")
        self._selected_id = None
        self._form_msg.configure(text="")

    # ── records ───────────────────────────────────────────────────────────────
    def _build_records(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")

        hdr = ctk.CTkFrame(f, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(hdr, text="All Records",
                     font=("Segoe UI", 24, "bold")).pack(side="left")
        ctk.CTkButton(hdr, text="🔄 Refresh", width=110, height=34,
                      corner_radius=8, fg_color="#2a2a4a",
                      hover_color="#3a3a5a",
                      command=self._load_records).pack(side="right")

        cols = ("ID", "Name", "Student ID", "Department", "Email", "Phone", "CGPA")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background="#16213e", foreground="#dddddd",
                        rowheight=32, fieldbackground="#16213e",
                        borderwidth=0, font=("Segoe UI", 12))
        style.configure("Custom.Treeview.Heading",
                        background="#1a1a2e", foreground="#7c83fd",
                        font=("Segoe UI", 12, "bold"), relief="flat")
        style.map("Custom.Treeview", background=[("selected", "#2a2a5a")])

        tree_frame = ctk.CTkFrame(f, fg_color=("#16213e","#16213e"),
                                  corner_radius=12)
        tree_frame.pack(fill="both", expand=True)

        self._tree = ttk.Treeview(tree_frame, columns=cols,
                                   show="headings", style="Custom.Treeview")
        widths = [50, 160, 110, 110, 180, 120, 70]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        vsb.pack(side="right", fill="y", pady=4)

        btn_row = ctk.CTkFrame(f, fg_color="transparent")
        btn_row.pack(fill="x", pady=12)
        ctk.CTkButton(btn_row, text="✏  Edit Selected",
                      width=160, height=38, corner_radius=10,
                      fg_color="#7c83fd", hover_color="#5a62e0",
                      command=self._edit_selected).pack(side="left", padx=6)
        ctk.CTkButton(btn_row, text="🗑  Delete Selected",
                      width=160, height=38, corner_radius=10,
                      fg_color="#ff6b6b", hover_color="#cc4444",
                      command=self._delete_selected).pack(side="left", padx=6)
        return f

    def _load_records(self, rows=None):
        self._tree.delete(*self._tree.get_children())
        data = rows if rows is not None else database.get_all_students()
        for row in data:
            self._tree.insert("", "end", values=row)

    def _edit_selected(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Edit", "Please select a student first.")
            return
        vals = self._tree.item(sel[0])["values"]
        self._selected_id = vals[0]
        self._clear_form()
        self._e_name.insert(0, vals[1])
        self._e_sid.insert(0, vals[2])
        self._dept_var.set(vals[3])
        self._e_email.insert(0, vals[4])
        self._e_phone.insert(0, vals[5])
        self._e_cgpa.insert(0, vals[6])
        self._show_tab("add")
        self._form_msg.configure(
            text="✏ Editing existing record — press Save to update.",
            text_color="#ffd93d")

    def _delete_selected(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Please select a student first.")
            return
        vals = self._tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirm", f"Delete {vals[1]}?"):
            database.delete_student(vals[0])
            self._load_records()

    # ── search ────────────────────────────────────────────────────────────────
    def _build_search(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")

        ctk.CTkLabel(f, text="Search Students",
                     font=("Segoe UI", 24, "bold")).pack(anchor="w", pady=(0, 16))

        bar = ctk.CTkFrame(f, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 16))
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._do_search())
        ctk.CTkEntry(bar, textvariable=self._search_var,
                     placeholder_text="Search by name, ID or department…",
                     height=42, corner_radius=10,
                     font=("Segoe UI", 14)).pack(
                         side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(bar, text="Search", width=100, height=42,
                      corner_radius=10, fg_color="#7c83fd",
                      hover_color="#5a62e0",
                      command=self._do_search).pack(side="left")

        cols = ("ID","Name","Student ID","Department","Email","Phone","CGPA")
        sf = ctk.CTkFrame(f, fg_color=("#16213e","#16213e"), corner_radius=12)
        sf.pack(fill="both", expand=True)

        self._stree = ttk.Treeview(sf, columns=cols,
                                    show="headings", style="Custom.Treeview")
        widths = [50, 160, 110, 110, 180, 120, 70]
        for col, w in zip(cols, widths):
            self._stree.heading(col, text=col)
            self._stree.column(col, width=w, anchor="center")

        vsb2 = ttk.Scrollbar(sf, orient="vertical",
                              command=self._stree.yview)
        self._stree.configure(yscrollcommand=vsb2.set)
        self._stree.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        vsb2.pack(side="right", fill="y", pady=4)

        self._search_count = ctk.CTkLabel(f, text="",
                                           font=("Segoe UI", 12),
                                           text_color="#aaa")
        self._search_count.pack(anchor="w", pady=6)
        return f

    def _do_search(self):
        q = self._search_var.get().strip()
        rows = database.search_students(q) if q else database.get_all_students()
        self._stree.delete(*self._stree.get_children())
        for row in rows:
            self._stree.insert("", "end", values=row)
        self._search_count.configure(text=f"{len(rows)} result(s) found")


# ── run ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.mainloop()