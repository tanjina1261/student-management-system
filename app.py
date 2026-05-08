import customtkinter as ctk
from tkinter import ttk, messagebox
import database

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DEPARTMENTS = ["CSE", "EEE", "BBA", "Civil",
               "Textile", "Pharmacy", "Law", "English"]

def make_entry(parent, placeholder, row, col,
               colspan=1, width=200):
    e = ctk.CTkEntry(
        parent, placeholder_text=placeholder,
        width=width, height=38, corner_radius=8,
        font=("Segoe UI", 13))
    e.grid(row=row, column=col, columnspan=colspan,
           padx=8, pady=6, sticky="ew")
    return e

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
        self.update()
        self.after(200, lambda: self._show_tab("dashboard"))

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=200, corner_radius=0,
                          fg_color="#1a1a2e")
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)
        ctk.CTkLabel(sb, text="📚 SMS",
                     font=("Segoe UI", 22, "bold"),
                     text_color="#7c83fd").pack(pady=(30, 4))
        ctk.CTkLabel(sb, text="Student Portal",
                     font=("Segoe UI", 11),
                     text_color="#888").pack(pady=(0, 30))
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
                command=lambda k=key: self._show_tab(k))
            btn.pack(pady=3, padx=14)
            self._nav_btns[key] = btn
        ctk.CTkFrame(sb, height=1,
                     fg_color="#333").pack(fill="x", padx=14, pady=20)
        ctk.CTkLabel(sb, text="v2.0  •  SQLite",
                     font=("Segoe UI", 10),
                     text_color="#555").pack(side="bottom", pady=16)

    def _build_main(self):
        self._main = ctk.CTkFrame(
            self, corner_radius=0, fg_color="#0f0f1a")
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
        self._frames[key].pack(
            fill="both", expand=True, padx=24, pady=24)
        for k, btn in self._nav_btns.items():
            btn.configure(
                fg_color="#2a2a4a" if k == key else "transparent",
                text_color="#ffffff" if k == key else "#cccccc")
        if key == "dashboard":
            self._refresh_dashboard()
        if key == "records":
            self._load_records()

    def _build_dashboard(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(f, text="Dashboard",
                     font=("Segoe UI", 24, "bold")).pack(
            anchor="w", pady=(0, 20))
        self._stat_row = ctk.CTkFrame(f, fg_color="transparent")
        self._stat_row.pack(fill="x", pady=(0, 24))
        self._dept_frame = ctk.CTkScrollableFrame(
            f, label_text="Students by Department",
            label_font=("Segoe UI", 14, "bold"),
            fg_color="#16213e", corner_radius=12)
        self._dept_frame.pack(fill="both", expand=True)
        return f

    def _stat_card(self, parent, title, value, color):
        card = ctk.CTkFrame(parent, fg_color="#16213e",
                            corner_radius=12)
        card.pack(side="left", expand=True,
                  fill="both", padx=6, pady=4)
        ctk.CTkLabel(card, text=str(value),
                     font=("Segoe UI", 36, "bold"),
                     text_color=color).pack(pady=(18, 2))
        ctk.CTkLabel(card, text=title,
                     font=("Segoe UI", 12),
                     text_color="#aaa").pack(pady=(0, 18))

    def _refresh_dashboard(self):
        for w in self._stat_row.winfo_children():
            w.destroy()
        for w in self._dept_frame.winfo_children():
            w.destroy()
        total, dept_counts, avg_credit = database.get_stats()
        self._stat_card(self._stat_row,
                        "Total Students", total, "#7c83fd")
        self._stat_card(self._stat_row,
                        "Departments", len(dept_counts), "#4ecdc4")
        self._stat_card(self._stat_row,
                        "System Status", "Online", "#44cf6c")
        colors = ["#7c83fd","#4ecdc4","#ff6b6b","#ffd93d",
                  "#44cf6c","#f7971e","#a8edea","#ee9ca7"]
        for i, (dept, count) in enumerate(dept_counts):
            row = ctk.CTkFrame(
                self._dept_frame, fg_color="transparent")
            row.pack(fill="x", pady=5, padx=10)
            ctk.CTkLabel(row, text=dept, width=120,
                         font=("Segoe UI", 13),
                         anchor="w").pack(side="left")
            bar_bg = ctk.CTkFrame(row, height=18,
                                  corner_radius=9,
                                  fg_color="#2a2a4a")
            bar_bg.pack(side="left", fill="x",
                        expand=True, padx=(0, 10))
            bar_bg.update_idletasks()
            w = max(40, int((count / max(total, 1)) * 300))
            ctk.CTkFrame(bar_bg, width=w, height=18,
                         corner_radius=9,
                         fg_color=colors[i % len(colors)]
                         ).place(x=0, y=0)
            ctk.CTkLabel(row, text=str(count),
                         font=("Segoe UI", 13, "bold"),
                         text_color=colors[i % len(colors)]
                         ).pack(side="left")

    def _build_add(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(f, text="Add / Edit Student",
                     font=("Segoe UI", 24, "bold")).pack(
            anchor="w", pady=(0, 16))
        form = ctk.CTkFrame(f, fg_color="#16213e",
                            corner_radius=14)
        form.pack(fill="x")
        form.columnconfigure((0, 1), weight=1)

        self._e_name  = make_entry(form, "Full Name",   0, 0)
        self._e_sid   = make_entry(form, "Student ID",  0, 1)
        self._e_email = make_entry(form, "Email",       1, 0)
        self._e_phone = make_entry(form, "Phone",       1, 1)
        self._e_cgpa  = make_entry(form, "CGPA (0–4)",  2, 0)

        self._dept_var = ctk.StringVar(value="CSE")
        ctk.CTkOptionMenu(
            form, values=DEPARTMENTS,
            variable=self._dept_var,
            width=200, height=38, corner_radius=8,
            font=("Segoe UI", 13)
        ).grid(row=2, column=1, padx=8, pady=6, sticky="ew")

        credit_frame = ctk.CTkFrame(form, fg_color="#1e2a4a",
                                    corner_radius=10)
        credit_frame.grid(row=3, column=0, columnspan=2,
                          padx=8, pady=(10, 4), sticky="ew")
        credit_frame.columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(credit_frame,
                     text="🎓  Credit Information",
                     font=("Segoe UI", 12, "bold"),
                     text_color="#7c83fd").grid(
            row=0, column=0, columnspan=3,
            padx=12, pady=(10, 4), sticky="w")

        self._e_earned = make_entry(
            credit_frame, "Earned Credit (e.g. 90)",
            1, 0, width=180)
        self._e_total  = make_entry(
            credit_frame, "Total Credit (e.g. 160)",
            1, 1, width=180)

        self._credit_label = ctk.CTkLabel(
            credit_frame, text="Progress: —",
            font=("Segoe UI", 11), text_color="#aaa")
        self._credit_label.grid(
            row=2, column=0, columnspan=3,
            padx=12, pady=(0, 4), sticky="w")

        self._credit_bar = ctk.CTkProgressBar(
            credit_frame, width=300, height=12,
            corner_radius=6,
            progress_color="#7c83fd",
            fg_color="#2a2a4a")
        self._credit_bar.grid(
            row=3, column=0, columnspan=3,
            padx=12, pady=(0, 12), sticky="ew")
        self._credit_bar.set(0)

        self._e_earned.bind(
            "<KeyRelease>", lambda e: self._update_credit_bar())
        self._e_total.bind(
            "<KeyRelease>", lambda e: self._update_credit_bar())

        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.grid(row=4, column=0, columnspan=2, pady=14)
        ctk.CTkButton(
            btn_row, text="💾  Save Student",
            width=180, height=40, corner_radius=10,
            font=("Segoe UI", 13, "bold"),
            fg_color="#7c83fd", hover_color="#5a62e0",
            command=self._save_student).pack(
                side="left", padx=8)
        ctk.CTkButton(
            btn_row, text="🗑  Clear Form",
            width=140, height=40, corner_radius=10,
            font=("Segoe UI", 13),
            fg_color="#2a2a4a", hover_color="#3a3a5a",
            command=self._clear_form).pack(
                side="left", padx=8)
        self._form_msg = ctk.CTkLabel(
            f, text="", font=("Segoe UI", 13))
        self._form_msg.pack(pady=10)
        return f

    def _update_credit_bar(self):
        try:
            earned = float(self._e_earned.get())
            total  = float(self._e_total.get())
            if total > 0:
                ratio = min(earned / total, 1.0)
                self._credit_bar.set(ratio)
                pct = ratio * 100
                color = ("#44cf6c" if pct >= 75
                         else "#ffd93d" if pct >= 50
                         else "#ff6b6b")
                self._credit_bar.configure(progress_color=color)
                self._credit_label.configure(
                    text=f"Progress: {earned:.0f} / "
                         f"{total:.0f} credits  "
                         f"({pct:.1f}%)",
                    text_color=color)
            else:
                self._credit_bar.set(0)
        except ValueError:
            self._credit_bar.set(0)
            self._credit_label.configure(
                text="Progress: —", text_color="#aaa")

    def _save_student(self):
        name   = self._e_name.get().strip()
        sid    = self._e_sid.get().strip()
        email  = self._e_email.get().strip()
        phone  = self._e_phone.get().strip()
        cgpa   = self._e_cgpa.get().strip()
        dept   = self._dept_var.get()
        earned = self._e_earned.get().strip()
        total  = self._e_total.get().strip()

        if not all([name, sid, email, phone, cgpa, earned, total]):
            self._form_msg.configure(
                text="⚠ Please fill all fields.",
                text_color="#ff6b6b")
            return
        try:
            e_val = int(earned)
            t_val = int(total)
            if e_val < 0 or t_val <= 0 or e_val > t_val:
                raise ValueError
        except ValueError:
            self._form_msg.configure(
                text="⚠ Credits must be valid numbers (earned ≤ total).",
                text_color="#ff6b6b")
            return

        if self._selected_id:
            ok, msg = database.update_student(
                self._selected_id, name, sid, dept,
                email, phone, cgpa, e_val, t_val)
            self._selected_id = None
        else:
            ok, msg = database.add_student(
                name, sid, dept, email, phone,
                cgpa, e_val, t_val)

        self._form_msg.configure(
            text=msg,
            text_color="#44cf6c" if ok else "#ff6b6b")
        if ok:
            self._clear_form()

    def _clear_form(self):
        for e in [self._e_name, self._e_sid, self._e_email,
                  self._e_phone, self._e_cgpa,
                  self._e_earned, self._e_total]:
            e.delete(0, "end")
        self._dept_var.set("CSE")
        self._selected_id = None
        self._form_msg.configure(text="")
        self._credit_bar.set(0)
        self._credit_label.configure(
            text="Progress: —", text_color="#aaa")

    def _build_records(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        hdr = ctk.CTkFrame(f, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(hdr, text="All Records",
                     font=("Segoe UI", 24, "bold")).pack(side="left")
        ctk.CTkButton(
            hdr, text="🔄 Refresh", width=110, height=34,
            corner_radius=8, fg_color="#2a2a4a",
            hover_color="#3a3a5a",
            command=self._load_records).pack(side="right")

        cols = ("ID", "Name", "Student ID", "Dept",
                "Email", "Phone", "CGPA",
                "Earned Cr", "Total Cr", "Progress")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview",
            background="#16213e", foreground="#dddddd",
            rowheight=32, fieldbackground="#16213e",
            borderwidth=0, font=("Segoe UI", 12))
        style.configure(
            "Custom.Treeview.Heading",
            background="#1a1a2e", foreground="#7c83fd",
            font=("Segoe UI", 12, "bold"), relief="flat")
        style.map("Custom.Treeview",
                  background=[("selected", "#2a2a5a")])

        tf = ctk.CTkFrame(f, fg_color="#16213e", corner_radius=12)
        tf.pack(fill="both", expand=True)
        self._tree = ttk.Treeview(
            tf, columns=cols,
            show="headings", style="Custom.Treeview")
        widths = [40, 140, 100, 80, 160, 110, 60, 80, 80, 90]
        for col, w in zip(cols, widths):
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w, anchor="center")
        vsb = ttk.Scrollbar(
            tf, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=vsb.set)
        self._tree.pack(side="left", fill="both",
                        expand=True, padx=4, pady=4)
        vsb.pack(side="right", fill="y", pady=4)

        btn_row = ctk.CTkFrame(f, fg_color="transparent")
        btn_row.pack(fill="x", pady=12)
        ctk.CTkButton(
            btn_row, text="✏  Edit Selected",
            width=160, height=38, corner_radius=10,
            fg_color="#7c83fd", hover_color="#5a62e0",
            command=self._edit_selected).pack(side="left", padx=6)
        ctk.CTkButton(
            btn_row, text="🗑  Delete Selected",
            width=160, height=38, corner_radius=10,
            fg_color="#ff6b6b", hover_color="#cc4444",
            command=self._delete_selected).pack(side="left", padx=6)
        return f

    def _load_records(self, rows=None):
        self._tree.delete(*self._tree.get_children())
        data = (rows if rows is not None
                else database.get_all_students())
        for row in data:
            (rid, name, sid, dept, email,
             phone, cgpa, earned, total) = row
            try:
                pct = (int(earned) / int(total) * 100
                       if int(total) > 0 else 0)
                progress = f"{pct:.0f}%"
            except:
                progress = "—"
            self._tree.insert("", "end", values=(
                rid, name, sid, dept, email,
                phone, cgpa, earned, total, progress))

    def _edit_selected(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo(
                "Edit", "Please select a student first.")
            return
        vals = self._tree.item(sel[0])["values"]
        self._selected_id = vals[0]
        self._clear_form()
        fields = [
            (self._e_name,   vals[1]),
            (self._e_sid,    vals[2]),
            (self._e_email,  vals[4]),
            (self._e_phone,  vals[5]),
            (self._e_cgpa,   vals[6]),
            (self._e_earned, vals[7]),
            (self._e_total,  vals[8]),
        ]
        for entry, val in fields:
            entry.insert(0, val)
        self._dept_var.set(vals[3])
        self._update_credit_bar()
        self._show_tab("add")
        self._form_msg.configure(
            text="✏ Editing record — press Save to update.",
            text_color="#ffd93d")

    def _delete_selected(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo(
                "Delete", "Please select a student first.")
            return
        vals = self._tree.item(sel[0])["values"]
        if messagebox.askyesno("Confirm", f"Delete {vals[1]}?"):
            database.delete_student(vals[0])
            self._load_records()

    def _build_search(self, parent):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        ctk.CTkLabel(f, text="Search Students",
                     font=("Segoe UI", 24, "bold")).pack(
            anchor="w", pady=(0, 16))
        bar = ctk.CTkFrame(f, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 16))
        self._search_var = ctk.StringVar()
        self._search_var.trace_add(
            "write", lambda *_: self._do_search())
        ctk.CTkEntry(
            bar, textvariable=self._search_var,
            placeholder_text="Search by name, ID or department…",
            height=42, corner_radius=10,
            font=("Segoe UI", 14)).pack(
                side="left", fill="x",
                expand=True, padx=(0, 10))
        ctk.CTkButton(
            bar, text="Search", width=100, height=42,
            corner_radius=10, fg_color="#7c83fd",
            hover_color="#5a62e0",
            command=self._do_search).pack(side="left")

        cols = ("ID", "Name", "Student ID", "Dept",
                "Email", "Phone", "CGPA",
                "Earned Cr", "Total Cr", "Progress")
        sf = ctk.CTkFrame(f, fg_color="#16213e", corner_radius=12)
        sf.pack(fill="both", expand=True)
        self._stree = ttk.Treeview(
            sf, columns=cols,
            show="headings", style="Custom.Treeview")
        widths = [40, 140, 100, 80, 160, 110, 60, 80, 80, 90]
        for col, w in zip(cols, widths):
            self._stree.heading(col, text=col)
            self._stree.column(col, width=w, anchor="center")
        vsb2 = ttk.Scrollbar(
            sf, orient="vertical",
            command=self._stree.yview)
        self._stree.configure(yscrollcommand=vsb2.set)
        self._stree.pack(side="left", fill="both",
                         expand=True, padx=4, pady=4)
        vsb2.pack(side="right", fill="y", pady=4)
        self._search_count = ctk.CTkLabel(
            f, text="", font=("Segoe UI", 12),
            text_color="#aaa")
        self._search_count.pack(anchor="w", pady=6)
        return f

    def _do_search(self):
        q = self._search_var.get().strip()
        rows = (database.search_students(q)
                if q else database.get_all_students())
        self._stree.delete(*self._stree.get_children())
        for row in rows:
            (rid, name, sid, dept, email,
             phone, cgpa, earned, total) = row
            try:
                pct = (int(earned) / int(total) * 100
                       if int(total) > 0 else 0)
                progress = f"{pct:.0f}%"
            except:
                progress = "—"
            self._stree.insert("", "end", values=(
                rid, name, sid, dept, email,
                phone, cgpa, earned, total, progress))
        self._search_count.configure(
            text=f"{len(rows)} result(s) found")


if __name__ == "__main__":
    app = App()
    app.mainloop()