#!/usr/bin/env python3
"""
Church Tithing Accounting App
A simple application for tracking church tithings and contributions.
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import json
import os
from datetime import datetime
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas as pdfcanvas
    from reportlab.lib.units import inch
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


DATA_FILE = "tither_data.json"


class TitherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tither - Church Tithing Tracker")
        self.root.geometry("900x600")
        self.root.configure(bg="#1e1e1e")

        self.in_search = False

        self.dark_theme()
        self.load_data()
        self.create_widgets()

    def dark_theme(self):
        self.colors = {
            "bg": "#1e1e1e",
            "fg": "#ffffff",
            "accent": "#4a90d9",
            "entry_bg": "#2d2d2d",
            "tree_bg": "#252525",
            "tree_fg": "#ffffff",
            "highlight": "#3c3c3c",
            "button": "#4a90d9",
            "button_fg": "#ffffff",
        }

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(".", background=self.colors["bg"], foreground=self.colors["fg"])
        style.configure(
            "Treeview",
            background=self.colors["tree_bg"],
            foreground=self.colors["tree_fg"],
            fieldbackground=self.colors["tree_bg"],
            rowheight=28,
        )
        style.configure(
            "Treeview.Heading",
            background=self.colors["accent"],
            foreground=self.colors["button_fg"],
            font=("Segoe UI", 10, "bold"),
        )
        style.map(
            "Treeview", background=[("selected", self.colors["accent"])]
        )

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {"churches": {}}
        self.labels = self.data.get("labels", {})

    def save_data(self):
        self.data["labels"] = self.labels
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    def get_label(self, key, default=None):
        return self.labels.get(key, default if default is not None else self.DEFAULT_LABELS.get(key, key))

    DEFAULT_LABELS = {
        "tax_receipt_title": "TAX RECEIPT",
        "tax_receipt_subtitle": "Tithe/Offering Contribution Record",
        "contribution_history": "Contribution History:",
        "total_contributions": "TOTAL CONTRIBUTIONS:",
        "tax_disclaimer1": "This letter serves as a receipt for income tax purposes.",
        "tax_disclaimer2": "No goods or services were provided in exchange for these contributions.",
    }

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        title_label = tk.Label(
            main_frame,
            text="Tither - Church Tithing Tracker",
            font=("Segoe UI", 18, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
        )
        title_label.pack(pady=(0, 20))

        self.title_label = title_label

        control_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.control_frame = control_frame

        self.btn_add_church = tk.Button(
            control_frame,
            text="+ Add Church",
            bg=self.colors["button"],
            fg=self.colors["button_fg"],
            command=self.add_church,
            relief=tk.FLAT,
            padx=15,
            pady=5,
        )
        self.btn_add_church.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_add_member = tk.Button(
            control_frame,
            text="+ Add Member/Family",
            bg=self.colors["button"],
            fg=self.colors["button_fg"],
            command=self.add_member,
            relief=tk.FLAT,
            padx=15,
            pady=5,
        )
        self.btn_add_member.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_record_tithe = tk.Button(
            control_frame,
            text="Record Tithe",
            bg=self.colors["button"],
            fg=self.colors["button_fg"],
            command=self.record_tithe,
            relief=tk.FLAT,
            padx=15,
            pady=5,
        )
        self.btn_record_tithe.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_settings = tk.Button(
            control_frame,
            text="Settings",
            bg=self.colors["button"],
            fg=self.colors["button_fg"],
            command=self.show_settings,
            relief=tk.FLAT,
            padx=15,
            pady=5,
        )
        self.btn_settings.pack(side=tk.LEFT)

        year_frame = tk.Frame(control_frame, bg=self.colors["bg"])
        year_frame.pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(year_frame, text="Year:", bg=self.colors["bg"], fg=self.colors["fg"]).pack(side=tk.LEFT, padx=(0, 5))
        self.year_var = tk.StringVar(value=str(datetime.now().year))
        self.year_combo = ttk.Combobox(year_frame, textvariable=self.year_var, width=6, state="readonly")
        self.year_combo.pack(side=tk.LEFT, padx=(0, 10))
        self.year_combo.bind("<<ComboboxSelected>>", self.on_year_change)

        self.active_only_var = tk.BooleanVar(value=True)
        self.active_only_cb = tk.Checkbutton(
            year_frame,
            text="Only active",
            variable=self.active_only_var,
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            selectcolor=self.colors["bg"],
            command=self.on_year_change,
        )
        self.active_only_cb.pack(side=tk.LEFT)

        search_frame = tk.Frame(control_frame, bg=self.colors["bg"])
        search_frame.pack(side=tk.RIGHT)

        self.search_frame = search_frame
        tk.Label(search_frame, text="Search:", bg=self.colors["bg"], fg=self.colors["fg"]).pack(
            side=tk.LEFT, padx=(0, 5)
        )
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg=self.colors["entry_bg"],
            fg=self.colors["fg"],
            insertbackground=self.colors["fg"],
            relief=tk.FLAT,
            width=25,
        )
        self.search_entry.pack(side=tk.LEFT)
        self.search_entry.bind("<KeyRelease>", self.on_search)
        self.search_entry.bind("<FocusIn>", self.on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self.on_search_focus_out)

        tree_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        tree_frame.pack(fill=tk.BOTH, expand=True)

        self.tree_frame = tree_frame

        columns = ("church", "member", "type", "amount", "date", "notes")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings", selectmode="browse")

        self.tree.heading("#0", text="ID")
        self.tree.heading("church", text="Church")
        self.tree.heading("member", text="Member/Family")
        self.tree.heading("type", text="Type")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("date", text="Date")
        self.tree.heading("notes", text="Notes")

        self.tree.column("#0", width=50, minwidth=50)
        self.tree.column("church", width=150, minwidth=100)
        self.tree.column("member", width=150, minwidth=100)
        self.tree.column("type", width=100, minwidth=80)
        self.tree.column("amount", width=100, minwidth=80)
        self.tree.column("date", width=100, minwidth=80)
        self.tree.column("notes", width=200, minwidth=100)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.selected_church = None
        self.selected_member = None
        self.selected_item_type = None
        self.selected_item_id = None

        self.context_menu = tk.Menu(self.tree, tearoff=0, bg=self.colors["bg"], fg=self.colors["fg"])
        self.context_menu.add_command(label="Edit", command=self.on_context_edit)
        self.context_menu.add_command(label="Delete", command=self.on_context_delete)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Tax Report", command=self.generate_tax_report)
        self.tree.bind("<Button-3>", self.show_context_menu)

        self.root.bind("<Control-q>", lambda e: self.root.destroy())

        self.root.bind("<question>", self.show_key_bindings)
        self.root.bind("<C>", self.on_key_c)
        self.root.bind("<c>", self.on_key_c_lower)
        self.root.bind("<A>", self.on_key_a)
        self.root.bind("<a>", self.on_key_a_lower)
        self.root.bind("<d>", self.on_key_d)
        self.root.bind("<D>", self.on_key_d)
        self.root.bind("<i>", self.on_key_i)
        self.root.bind("<I>", self.on_key_i)
        self.root.bind("<r>", self.on_key_r)
        self.root.bind("<R>", self.on_key_r)
        self.root.bind("<at>", self.on_key_at)
        self.focus_tree()

        status_frame = tk.Frame(main_frame, bg=self.colors["bg"])
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_frame = status_frame
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            bg=self.colors["bg"],
            fg=self.colors["fg"],
            anchor=tk.W,
        )
        self.status_label.pack(side=tk.LEFT)

        self.populate_tree()
        self.focus_tree()

    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        search_term = self.search_var.get().lower()
        selected_year = self.year_var.get()
        active_only = self.active_only_var.get()

        self.update_available_years()

        for church_name, church_data in self.data["churches"].items():
            church_node = self.tree.insert("", tk.END, text="", values=(church_name, "", "", "", "", ""))
            self.tree.item(church_node, open=True)

            members = church_data.get("members", {})
            tithes = church_data.get("tithes", [])

            for member_id, member_data in members.items():
                member_name = member_data.get("name", "Unknown")

                if search_term and search_term not in member_name.lower() and search_term not in church_name.lower():
                    continue

                member_tithes = [t for t in tithes if t.get("member_id") == member_id and t.get("date", "").startswith(selected_year)]

                if active_only and not member_tithes:
                    continue

                member_node = self.tree.insert(
                    church_node,
                    tk.END,
                    text=member_id[:8],
                    values=(church_name, member_name, "", "", "", ""),
                )

                for tithe in member_tithes:
                    amount = f"${tithe.get('amount', 0):.2f}"
                    date = tithe.get("date", "")
                    notes = tithe.get("notes", "")
                    self.tree.insert(
                            member_node,
                            tk.END,
                            text=tithe.get("id", "")[:8],
                            values=(
                                church_name,
                                member_name,
                                "Tithe",
                                amount,
                                date,
                                notes,
                            ),
                        )

    def update_available_years(self):
        years = set()
        current_year = self.year_var.get()
        for church_data in self.data["churches"].values():
            for tithe in church_data.get("tithes", []):
                date = tithe.get("date", "")
                if date:
                    years.add(date[:4])
        if years:
            self.year_combo["values"] = sorted(years, reverse=True)
            if current_year not in years:
                self.year_combo.current(0)
                self.year_var.set(self.year_combo.get())

    def on_year_change(self, event=None):
        self.populate_tree()

    def on_search(self, event=None):
        self.populate_tree()

    def focus_tree(self):
        self.tree.focus_set()
        children = self.tree.get_children()
        if children:
            self.tree.selection_set(children[0])
            self.tree.see(children[0])

    def on_search_focus_in(self, event=None):
        self.in_search = True

    def on_search_focus_out(self, event=None):
        self.in_search = False
        self.focus_tree()

    def show_key_bindings(self, event=None):
        if self.in_search:
            self.focus_tree()
            return "break"
        bindings = """KEY BINDINGS:
? - Show this help
c - Create new Church (any case)
A - Create new Member
a - Record a Tithe
D - Delete selected item
I - Edit selected item
R - Tax Report
@ - Toggle active only
Ctrl+Q - Quit"""
        popup = tk.Toplevel(self.root)
        popup.title("Keyboard Shortcuts")
        popup.geometry("450x300")
        popup.configure(bg=self.colors["bg"])
        popup.bind("<Escape>", lambda e: popup.destroy())
        txt = tk.Text(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], font=("Consolas", 11), relief=tk.FLAT)
        txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        txt.insert("1.0", bindings)
        txt.config(state=tk.DISABLED)

    def on_key_c(self, event=None):
        if self.in_search:
            return "break"
        self.add_church()

    def on_key_c_lower(self, event=None):
        if self.in_search:
            return "break"
        self.add_church()

    def on_key_a(self, event=None):
        if self.in_search:
            return "break"
        self.add_member()

    def on_key_a_lower(self, event=None):
        if self.in_search:
            return "break"
        self.record_tithe()

    def on_key_d(self, event=None):
        if self.in_search:
            return "break"
        if self.selected_item_type == "church":
            self.delete_church(self.selected_church)
        elif self.selected_item_type == "member":
            mid = self.find_member_id_by_name(self.selected_church, self.selected_member)
            self.delete_member(self.selected_church, self.selected_member, mid)
        elif self.selected_item_type == "tithe":
            church = None
            for sel in self.tree.selection():
                vals = self.tree.item(sel).get("values", [])
                if vals:
                    church = vals[0]
            self.delete_tithe(church, self.selected_tithe_id)

    def on_key_i(self, event=None):
        if self.in_search:
            return "break"
        if self.selected_item_type == "church":
            self.edit_church(self.selected_church)
        elif self.selected_item_type == "member":
            mid = self.find_member_id_by_name(self.selected_church, self.selected_member)
            self.edit_member(self.selected_church, self.selected_member, mid)
        elif self.selected_item_type == "tithe":
            for sel in self.tree.selection():
                vals = self.tree.item(sel).get("values", [])
                tid = self.tree.item(sel).get("text", "")
                if vals and tid:
                    self.edit_tithe(vals[0], vals[1], tid, vals[3], vals[4], vals[5])

    def on_key_r(self, event=None):
        if self.in_search:
            return "break"
        if self.selected_item_type == "member":
            self.generate_tax_report()
        else:
            self.status_label.config(text="Select a member for tax report")

    def on_key_at(self, event=None):
        if self.in_search:
            return "break"
        self.active_only_var.set(not self.active_only_var.get())
        self.on_year_change()

    def show_settings(self):
        popup = tk.Toplevel(self.root)
        popup.title("Settings")
        popup.geometry("500x450")
        popup.configure(bg=self.colors["bg"])

        popup.bind("<Escape>", lambda e: popup.destroy())

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=self.colors["entry_bg"], background=self.colors["entry_bg"], foreground=self.colors["fg"], selectbackground=self.colors["entry_bg"])

        tk.Label(
            popup,
            text="Tax Report Labels",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
        ).pack(pady=15)

        fields = [
            ("tax_receipt_title", "Title"),
            ("tax_receipt_subtitle", "Subtitle"),
            ("contribution_history", "Contribution History Header"),
            ("total_contributions", "Total Label"),
            ("tax_disclaimer1", "Disclaimer Line 1"),
            ("tax_disclaimer2", "Disclaimer Line 2"),
        ]

        entries = {}
        for key, label in fields:
            tk.Label(popup, text=label + ":", bg=self.colors["bg"], fg=self.colors["fg"]).pack(anchor="w", padx=20, pady=(10, 0))
            entry = tk.Entry(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
            entry.pack(fill=tk.X, padx=20)
            entry.insert(0, self.get_label(key))
            entries[key] = entry

        btn_frame = tk.Frame(popup, bg=self.colors["bg"])
        btn_frame.pack(pady=20)

        def save_settings():
            for key, entry in entries.items():
                val = entry.get().strip()
                if val:
                    self.labels[key] = val
            self.save_data()
            self.status_label.config(text="Settings saved")
            popup.destroy()

        def revert_settings():
            if "labels" in self.data:
                del self.data["labels"]
            self.labels = {}
            self.save_data()
            for key, entry in entries.items():
                entry.delete(0, tk.END)
                entry.insert(0, self.DEFAULT_LABELS.get(key, key))
            self.status_label.config(text="Settings reverted to defaults")

        tk.Button(btn_frame, text="Save", bg=self.colors["button"], fg=self.colors["button_fg"], command=save_settings, relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Revert to Defaults", bg="#d94a4a", fg=self.colors["button_fg"], command=revert_settings, relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", bg="#666666", fg="#ffffff", command=popup.destroy, relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=5)

    def get_tithes_for_year(self, church_name, member_id, year):
        tithes = self.data["churches"].get(church_name, {}).get("tithes", [])
        return [t for t in tithes if t.get("member_id") == member_id and t.get("date", "").startswith(year)]

    def get_all_tithes_for_member(self, church_name, member_id):
        return [t for t in self.data["churches"].get(church_name, {}).get("tithes", []) if t.get("member_id") == member_id]

    def generate_report_text(self, church_name, member_name, member_address, member_tithes, total):
        lines = [
            self.get_label("tax_receipt_title"),
            self.get_label("tax_receipt_subtitle"),
            "",
            f"Church: {church_name}",
            f"Name: {member_name}",
        ]
        if member_address:
            lines.append(f"Address: {member_address}")
        lines.append("")
        lines.append(self.get_label("contribution_history"))
        lines.append("-" * 60)
        for tithe in sorted(member_tithes, key=lambda x: x.get("date", "")):
            date = tithe.get("date", "")
            amount = tithe.get("amount", 0)
            notes = tithe.get("notes", "")
            notes_part = f" ({notes})" if notes else ""
            lines.append(f"  {date}   ${amount:,.2f}{notes_part}")
        lines.append("-" * 60)
        lines.append(f"{self.get_label('total_contributions')} ${total:,.2f}")
        lines.append("")
        lines.append(self.get_label("tax_disclaimer1"))
        lines.append(self.get_label("tax_disclaimer2"))
        return "\n".join(lines)

    def add_church(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add Church")
        popup.geometry("400x250")
        popup.configure(bg=self.colors["bg"])

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=self.colors["entry_bg"], background=self.colors["entry_bg"], foreground=self.colors["fg"], selectbackground=self.colors["entry_bg"])

        popup.bind("<Escape>", lambda e: popup.destroy())

        tk.Label(
            popup,
            text="Add New Church",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
        ).pack(pady=15)

        tk.Label(popup, text="Church Name:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        name_entry = tk.Entry(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        name_entry.pack(pady=5, padx=20, fill=tk.X)

        tk.Label(popup, text="Address:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        address_entry = tk.Entry(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        address_entry.pack(pady=5, padx=20, fill=tk.X)

        def save_church():
            name = name_entry.get().strip()
            address = address_entry.get().strip()
            if name:
                self.data["churches"][name] = {
                    "address": address,
                    "members": {},
                    "tithes": [],
                }
                self.save_data()
                self.populate_tree()
                self.status_label.config(text=f"Church '{name}' added successfully")
                popup.destroy()
            else:
                self.status_label.config(text="Please enter a church name")

        tk.Button(
            popup,
            text="Save Church",
            bg=self.colors["button"],
            fg=self.colors["button_fg"],
            command=save_church,
            relief=tk.FLAT,
            padx=20,
            pady=5,
        ).pack(pady=15)

    def add_member(self):
        if not self.data["churches"]:
            self.status_label.config(text="Please add a church first")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Add Member/Family")
        popup.geometry("450x400")
        popup.configure(bg=self.colors["bg"])

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=self.colors["entry_bg"], background=self.colors["entry_bg"], foreground=self.colors["fg"], selectbackground=self.colors["entry_bg"])

        popup.bind("<Escape>", lambda e: popup.destroy())

        tk.Label(
            popup,
            text="Add Member/Family",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
        ).pack(pady=15)

        tk.Label(popup, text="Select Church:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        church_var = tk.StringVar()
        church_combo = ttk.Combobox(
            popup,
            textvariable=church_var,
            values=list(self.data["churches"].keys()),
            state="readonly",
        )
        church_combo.pack(pady=5, padx=20, fill=tk.X)
        if self.selected_church and self.selected_church in self.data["churches"]:
            church_combo.set(self.selected_church)
        elif self.data["churches"]:
            church_combo.current(0)

        tk.Label(popup, text="Name:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        name_entry = tk.Entry(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        name_entry.pack(pady=5, padx=20, fill=tk.X)

        tk.Label(popup, text="Address:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        address_entry = tk.Entry(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        address_entry.pack(pady=5, padx=20, fill=tk.X)

        def save_member():
            church = church_var.get()
            name = name_entry.get().strip()
            address = address_entry.get().strip()
            if church and name:
                import uuid

                member_id = str(uuid.uuid4())
                self.data["churches"][church]["members"][member_id] = {
                    "name": name,
                    "address": address,
                }
                self.save_data()
                self.populate_tree()
                self.status_label.config(text=f"Member '{name}' added to {church}")
                popup.destroy()
            else:
                self.status_label.config(text="Please select a church and enter a name")

        tk.Button(
            popup,
            text="Save Member",
            bg=self.colors["button"],
            fg=self.colors["button_fg"],
            command=save_member,
            relief=tk.FLAT,
            padx=20,
            pady=5,
        ).pack(pady=15)

    def record_tithe(self):
        if not self.data["churches"]:
            self.status_label.config(text="Please add a church and member first")
            return

        popup = tk.Toplevel(self.root)
        popup.title("Record Tithe")
        popup.geometry("450x400")
        popup.configure(bg=self.colors["bg"])

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=self.colors["entry_bg"], background=self.colors["entry_bg"], foreground=self.colors["fg"], selectbackground=self.colors["entry_bg"])

        popup.bind("<Escape>", lambda e: popup.destroy())

        tk.Label(
            popup,
            text="Record Tithe Payment",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
        ).pack(pady=15)

        tk.Label(popup, text="Select Church:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        church_var = tk.StringVar()
        church_combo = ttk.Combobox(
            popup,
            textvariable=church_var,
            values=list(self.data["churches"].keys()),
            state="readonly",
        )
        church_combo.pack(pady=5, padx=20, fill=tk.X)

        if self.selected_church and self.selected_church in self.data["churches"]:
            church_combo.set(self.selected_church)

        members_var = tk.StringVar()
        members_combo = ttk.Combobox(popup, textvariable=members_var, state="readonly")
        members_combo.pack(pady=5, padx=20, fill=tk.X)

        def update_members(*args):
            church = church_var.get()
            if church:
                members = self.data["churches"].get(church, {}).get("members", {})
                members_combo["values"] = [m.get("name", "") for m in members.values()]
                if self.selected_member and self.selected_member in members_combo["values"]:
                    members_combo.set(self.selected_member)

        church_var.trace("w", update_members)

        if self.selected_church:
            update_members()

        tk.Label(popup, text="Date:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        date_frame = tk.Frame(popup, bg=self.colors["bg"])
        date_frame.pack(pady=5, padx=20, fill=tk.X)

        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

        date_entry = tk.Entry(date_frame, textvariable=date_var, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"], width=12)
        date_entry.pack(side=tk.LEFT)

        def show_calendar():
            cal_win = tk.Toplevel(popup)
            cal_win.title("Select Date")
            cal_win.configure(bg=self.colors["bg"])
            current_date = date_var.get()
            try:
                year = int(current_date[:4])
                month = int(current_date[5:7])
                day = int(current_date[8:10])
            except:
                year = datetime.now().year
                month = datetime.now().month
                day = datetime.now().day
            cal = tk.Calendar(cal_win, year=year, month=month, day=day, selectmode="day")
            cal.pack(pady=10)
            def on_select():
                date_var.set(cal.selection_get().strftime("%Y-%m-%d"))
                cal_win.destroy()
            tk.Button(cal_win, text="Select", bg=self.colors["button"], fg=self.colors["button_fg"], command=on_select, relief=tk.FLAT).pack(pady=5)

        tk.Button(date_frame, text="Pick", bg=self.colors["button"], fg=self.colors["button_fg"], command=show_calendar, relief=tk.FLAT, padx=5).pack(side=tk.LEFT, padx=5)

        tk.Label(popup, text="Amount:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        amount_entry = tk.Entry(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        amount_entry.pack(pady=5, padx=20, fill=tk.X)

        tk.Label(popup, text="Notes:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        notes_entry = tk.Entry(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        notes_entry.pack(pady=5, padx=20, fill=tk.X)

        def save_tithe():
            church = church_var.get()
            member_name = members_var.get()
            amount_str = amount_entry.get().strip()
            notes = notes_entry.get().strip()
            tithe_date = date_var.get().strip()

            try:
                amount = float(amount_str)
            except ValueError:
                self.status_label.config(text="Please enter a valid amount")
                return

            if not church or not member_name:
                self.status_label.config(text="Please select church and member")
                return

            member_id = None
            for mid, mdata in self.data["churches"][church]["members"].items():
                if mdata.get("name") == member_name:
                    member_id = mid
                    break

            if member_id:
                import uuid

                tithe_id = str(uuid.uuid4())
                tithe = {
                    "id": tithe_id,
                    "member_id": member_id,
                    "amount": amount,
                    "date": tithe_date if tithe_date else datetime.now().strftime("%Y-%m-%d"),
                    "notes": notes,
                }
                self.data["churches"][church]["tithes"].append(tithe)
                self.save_data()
                self.populate_tree()
                self.status_label.config(text=f"Tithe of ${amount:.2f} recorded for {member_name}")
                popup.destroy()

        tk.Button(
            popup,
            text="Record Tithe",
            bg=self.colors["button"],
            fg=self.colors["button_fg"],
            command=save_tithe,
            relief=tk.FLAT,
            padx=20,
            pady=5,
        ).pack(pady=15)

    def on_tree_select(self, event=None):
        selection = self.tree.selection()
        self.selected_church = None
        self.selected_member = None
        self.selected_tithe_id = None
        self.selected_item_type = None
        self.selected_item_id = None
        if selection:
            item = self.tree.item(selection[0])
            values = item.get("values", [])
            self.selected_item_id = item.get("text", "")
            self.selected_tithe_id = self.selected_item_id
            if values and values[0]:
                self.selected_church = values[0]
            if values and values[1]:
                self.selected_member = values[1]
            if values and values[2] == "Tithe":
                self.selected_item_type = "tithe"
            elif values and values[0] and values[1] and not values[2]:
                self.selected_item_type = "member"
            elif values and values[0] and not values[1]:
                self.selected_item_type = "church"

    def show_context_menu(self, event):
        if self.tree.selection():
            self.context_menu.post(event.x_root, event.y_root)

    def find_member_id_by_name(self, church_name, member_name):
        members = self.data["churches"].get(church_name, {}).get("members", {})
        for mid, mdata in members.items():
            if mdata.get("name") == member_name:
                return mid
        return None

    def on_context_edit(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        values = item.get("values", [])
        item_id = item.get("text", "")
        if self.selected_item_type == "church" and values[0]:
            self.edit_church(values[0])
        elif self.selected_item_type == "member" and values[0] and values[1]:
            member_id = self.find_member_id_by_name(values[0], values[1])
            if member_id:
                self.edit_member(values[0], values[1], member_id)
        elif self.selected_item_type == "tithe" and values[0] and values[1] and item_id:
            self.edit_tithe(values[0], values[1], item_id, values[3], values[4], values[5])

    def on_context_delete(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        values = item.get("values", [])
        item_id = item.get("text", "")
        if self.selected_item_type == "church" and values[0]:
            self.delete_church(values[0])
        elif self.selected_item_type == "member" and values[0] and values[1]:
            self.delete_member(values[0], values[1], item_id)
        elif self.selected_item_type == "tithe" and values[0] and values[1] and item_id:
            self.delete_tithe(values[0], item_id)

    def edit_church(self, church_name):
        church_data = self.data["churches"].get(church_name, {})
        popup = tk.Toplevel(self.root)
        popup.title("Edit Church")
        popup.geometry("400x280")
        popup.configure(bg=self.colors["bg"])

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=self.colors["entry_bg"], background=self.colors["entry_bg"], foreground=self.colors["fg"], selectbackground=self.colors["entry_bg"])

        popup.bind("<Escape>", lambda e: popup.destroy())

        tk.Label(
            popup,
            text="Edit Church",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
        ).pack(pady=15)

        tk.Label(popup, text="Church Name:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        name_entry = tk.Entry(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        name_entry.pack(pady=5, padx=20, fill=tk.X)
        name_entry.insert(0, church_name)

        tk.Label(popup, text="Address:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        address_entry = tk.Entry(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        address_entry.pack(pady=5, padx=20, fill=tk.X)
        address_entry.insert(0, church_data.get("address", ""))

        btn_frame = tk.Frame(popup, bg=self.colors["bg"])
        btn_frame.pack(pady=15)

        def save():
            new_name = name_entry.get().strip()
            address = address_entry.get().strip()
            if new_name and new_name != church_name:
                self.data["churches"][new_name] = self.data["churches"].pop(church_name)
                self.data["churches"][new_name]["address"] = address
                self.selected_church = new_name
            else:
                self.data["churches"][church_name]["address"] = address
            self.save_data()
            self.populate_tree()
            self.status_label.config(text=f"Church '{new_name or church_name}' updated")
            popup.destroy()

        def delete():
            self.delete_church(church_name)
            popup.destroy()

        tk.Button(btn_frame, text="Save", bg=self.colors["button"], fg=self.colors["button_fg"], command=save, relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Church", bg="#d94a4a", fg=self.colors["button_fg"], command=delete, relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=5)

    def delete_church(self, church_name):
        if church_name in self.data["churches"]:
            del self.data["churches"][church_name]
            self.save_data()
            self.populate_tree()
            self.status_label.config(text=f"Church '{church_name}' deleted")

    def edit_member(self, church_name, member_name, member_id):
        member_data = self.data["churches"].get(church_name, {}).get("members", {}).get(member_id, {})
        popup = tk.Toplevel(self.root)
        popup.title("Edit Member")
        popup.geometry("450x400")
        popup.configure(bg=self.colors["bg"])

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=self.colors["entry_bg"], background=self.colors["entry_bg"], foreground=self.colors["fg"], selectbackground=self.colors["entry_bg"])

        popup.bind("<Escape>", lambda e: popup.destroy())

        tk.Label(
            popup,
            text="Edit Member/Family",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
        ).pack(pady=15)

        tk.Label(popup, text="Church:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        tk.Label(popup, text=church_name, bg=self.colors["bg"], fg=self.colors["fg"], font=("Segoe UI", 10, "bold")).pack()

        tk.Label(popup, text="Name:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        name_entry = tk.Entry(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        name_entry.pack(pady=5, padx=20, fill=tk.X)
        name_entry.insert(0, member_data.get("name", ""))

        tk.Label(popup, text="Address:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        address_entry = tk.Entry(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        address_entry.pack(pady=5, padx=20, fill=tk.X)
        address_entry.insert(0, member_data.get("address", ""))

        btn_frame = tk.Frame(popup, bg=self.colors["bg"])
        btn_frame.pack(pady=15)

        def save():
            new_name = name_entry.get().strip()
            address = address_entry.get().strip()
            if new_name:
                self.data["churches"][church_name]["members"][member_id] = {
                    "name": new_name,
                    "address": address,
                }
                self.save_data()
                self.populate_tree()
                self.status_label.config(text=f"Member '{new_name}' updated")
                popup.destroy()

        def delete():
            self.delete_member(church_name, member_name, member_id)
            popup.destroy()

        tk.Button(btn_frame, text="Save", bg=self.colors["button"], fg=self.colors["button_fg"], command=save, relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Member", bg="#d94a4a", fg=self.colors["button_fg"], command=delete, relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=5)

    def delete_member(self, church_name, member_name, member_id):
        if church_name in self.data["churches"] and member_id in self.data["churches"][church_name]["members"]:
            del self.data["churches"][church_name]["members"][member_id]
            self.data["churches"][church_name]["tithes"] = [t for t in self.data["churches"][church_name]["tithes"] if t.get("member_id") != member_id]
            self.save_data()
            self.populate_tree()
            self.status_label.config(text=f"Member '{member_name}' deleted")

    def delete_tithe(self, church_name, tithe_id):
        self.data["churches"][church_name]["tithes"] = [
            t for t in self.data["churches"][church_name]["tithes"]
            if t.get("id", "")[:8] != tithe_id
        ]
        self.save_data()
        self.populate_tree()
        self.status_label.config(text="Tithe deleted")

    def on_double_click(self, event=None):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        values = item.get("values", [])
        tithe_id = item.get("text", "")
        if not values or not values[3] or not tithe_id:
            return
        church_name = values[0]
        member_name = values[1]
        amount_str = values[3]
        date_str = values[4]
        notes_str = values[5]
        self.edit_tithe(church_name, member_name, tithe_id, amount_str, date_str, notes_str)

    def generate_tax_report(self):
        if self.selected_item_type != "member" or not self.selected_church or not self.selected_member:
            self.status_label.config(text="Please select a member to generate tax report")
            return

        church_name = self.selected_church
        member_name = self.selected_member
        member_id = self.find_member_id_by_name(church_name, member_name)
        if not member_id:
            return

        member_data = self.data["churches"].get(church_name, {}).get("members", {}).get(member_id, {})
        member_address = member_data.get("address", "")
        tithes = self.data["churches"].get(church_name, {}).get("tithes", [])
        member_tithes = [t for t in tithes if t.get("member_id") == member_id]

        report_win = tk.Toplevel(self.root)
        report_win.title(f"Tax Report - {member_name}")
        report_win.geometry("600x700")
        report_win.configure(bg="#ffffff")

        report_win.bind("<Escape>", lambda e: report_win.destroy())

        canvas = tk.Canvas(report_win, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(report_win, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ffffff")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        header_frame = tk.Frame(scrollable_frame, bg="#ffffff", padx=40, pady=30)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text=self.get_label("tax_receipt_title"), font=("Helvetica", 18, "bold"), bg="#ffffff", fg="#000000").pack()
        tk.Label(header_frame, text=self.get_label("tax_receipt_subtitle"), font=("Helvetica", 12), bg="#ffffff", fg="#333333").pack(pady=(5, 20))

        info_frame = tk.Frame(scrollable_frame, bg="#ffffff", padx=40, pady=10)
        info_frame.pack(fill=tk.X)
        church_info = self.data["churches"].get(church_name, {})
        tk.Label(info_frame, text=f"Church: {church_name}", font=("Helvetica", 11, "bold"), bg="#ffffff", fg="#000000").pack(anchor="w")
        if church_info.get("address"):
            tk.Label(info_frame, text=f"      {church_info.get('address')}", font=("Helvetica", 10), bg="#ffffff", fg="#333333").pack(anchor="w")

        tk.Label(info_frame, text="", bg="#ffffff").pack(pady=10)

        tk.Label(info_frame, text=f"Name: {member_name}", font=("Helvetica", 11, "bold"), bg="#ffffff", fg="#000000").pack(anchor="w")
        if member_address:
            tk.Label(info_frame, text=f"Address: {member_address}", font=("Helvetica", 10), bg="#ffffff", fg="#333333").pack(anchor="w")

        tk.Label(info_frame, text="", bg="#ffffff").pack(pady=10)

        tk.Label(info_frame, text=self.get_label("contribution_history"), font=("Helvetica", 11, "bold"), bg="#ffffff", fg="#000000").pack(anchor="w")
        tk.Label(info_frame, text="-" * 60, bg="#ffffff", fg="#333333").pack(anchor="w")

        total = 0.0
        for tithe in sorted(member_tithes, key=lambda x: x.get("date", ""), reverse=True):
            amount = tithe.get("amount", 0)
            date = tithe.get("date", "")
            notes = tithe.get("notes", "")
            total += amount
            tk.Label(info_frame, text=f"  {date}  ${amount:,.2f}  {notes}", font=("Helvetica", 10), bg="#ffffff", fg="#333333").pack(anchor="w")

        tk.Label(info_frame, text="-" * 60, bg="#ffffff", fg="#333333").pack(anchor="w")

        total_frame = tk.Frame(scrollable_frame, bg="#ffffff", padx=40, pady=20)
        total_frame.pack(fill=tk.X)
        tk.Label(total_frame, text=f"{self.get_label('total_contributions')} ${total:,.2f}", font=("Helvetica", 14, "bold"), bg="#ffffff", fg="#000000").pack(anchor="w")

        note_frame = tk.Frame(scrollable_frame, bg="#ffffff", padx=40, pady=20)
        note_frame.pack(fill=tk.X)
        tk.Label(note_frame, text=self.get_label("tax_disclaimer1"), font=("Helvetica", 10, "italic"), bg="#ffffff", fg="#333333").pack(anchor="w")
        tk.Label(note_frame, text=self.get_label("tax_disclaimer2"), font=("Helvetica", 10, "italic"), bg="#ffffff", fg="#333333").pack(anchor="w")

        footer_frame = tk.Frame(scrollable_frame, bg="#ffffff", padx=40, pady=30)
        footer_frame.pack(fill=tk.X)
        btn_frame = tk.Frame(footer_frame, bg="#ffffff")
        btn_frame.pack()

        def print_report():
            if not HAS_REPORTLAB:
                self.status_label.config(text="reportlab not installed. Run: pip install reportlab")
                return
            reports_dir = "reports"
            os.makedirs(reports_dir, exist_ok=True)
            pdf_file = os.path.join(reports_dir, f"{member_name.replace(' ', '_')}_tax_receipt.pdf")
            c = pdfcanvas.Canvas(pdf_file, pagesize=letter)
            width, height = letter

            y = height - 50
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, y, self.get_label("tax_receipt_title"))
            y -= 25
            c.setFont("Helvetica", 12)
            c.drawString(50, y, self.get_label("tax_receipt_subtitle"))
            y -= 35

            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, f"Church: {church_name}")
            church_info = self.data["churches"].get(church_name, {})
            if church_info.get("address"):
                y -= 15
                c.setFont("Helvetica", 10)
                c.drawString(50, y, church_info["address"])
            y -= 25

            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, f"Name: {member_name}")
            y -= 15
            if member_address:
                c.setFont("Helvetica", 10)
                c.drawString(50, y, f"Address: {member_address}")
            y -= 30

            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, self.get_label("contribution_history"))
            y -= 15
            c.line(50, y + 5, width - 50, y + 5)
            y -= 20

            c.setFont("Helvetica", 10)
            date_x = 55
            amount_x = 350
            for tithe in sorted(member_tithes, key=lambda x: x.get("date", "")):
                date = tithe.get("date", "")
                amount = tithe.get("amount", 0)
                notes = tithe.get("notes", "")
                c.drawString(date_x, y, date)
                c.drawRightString(amount_x, y, f"${amount:,.2f}")
                if notes:
                    c.drawString(amount_x + 10, y, f"({notes})")
                y -= 15

            c.line(50, y + 5, width - 50, y + 5)
            y -= 20

            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, self.get_label("total_contributions"))
            c.drawRightString(amount_x, y, f"${total:,.2f}")
            y -= 35

            c.setFont("Helvetica-Oblique", 10)
            c.drawString(50, y, self.get_label("tax_disclaimer1"))
            y -= 15
            c.drawString(50, y, self.get_label("tax_disclaimer2"))

            c.save()
            try:
                os.startfile(pdf_file, "print")
            except AttributeError:
                import subprocess
                try:
                    subprocess.Popen(["xdg-open", pdf_file])
                except:
                    subprocess.Popen(["open", pdf_file])
            self.status_label.config(text=f"PDF saved: {pdf_file}")

        tk.Button(btn_frame, text="Print", bg="#4a90d9", fg="#ffffff", command=print_report, relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Close", bg="#666666", fg="#ffffff", command=report_win.destroy, relief=tk.FLAT, padx=20, pady=5).pack(side=tk.LEFT, padx=5)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def edit_tithe(self, church_name, member_name, tithe_id, amount_str, date_str, notes_str):
        popup = tk.Toplevel(self.root)
        popup.title("Edit/Delete Tithe")
        popup.geometry("450x350")
        popup.configure(bg=self.colors["bg"])

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=self.colors["entry_bg"], background=self.colors["entry_bg"], foreground=self.colors["fg"], selectbackground=self.colors["entry_bg"])

        popup.bind("<Escape>", lambda e: popup.destroy())

        tk.Label(
            popup,
            text="Edit or Delete Tithe",
            font=("Segoe UI", 14, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["fg"],
        ).pack(pady=15)

        tk.Label(popup, text="Church:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        tk.Label(popup, text=church_name, bg=self.colors["bg"], fg=self.colors["fg"], font=("Segoe UI", 10, "bold")).pack()

        tk.Label(popup, text="Member:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        tk.Label(popup, text=member_name, bg=self.colors["bg"], fg=self.colors["fg"], font=("Segoe UI", 10, "bold")).pack()

        tk.Label(popup, text="Amount:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        amount_entry = tk.Entry(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        amount_entry.pack(pady=5, padx=20, fill=tk.X)
        amount_entry.insert(0, amount_str.replace("$", "").replace(",", ""))

        tk.Label(popup, text="Notes:", bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        notes_entry = tk.Entry(popup, bg=self.colors["entry_bg"], fg=self.colors["fg"], insertbackground=self.colors["fg"])
        notes_entry.pack(pady=5, padx=20, fill=tk.X)
        notes_entry.insert(0, notes_str)

        btn_frame = tk.Frame(popup, bg=self.colors["bg"])
        btn_frame.pack(pady=15)

        def save_edit():
            amount_val = amount_entry.get().strip()
            notes_val = notes_entry.get().strip()
            try:
                amount = float(amount_val)
            except ValueError:
                self.status_label.config(text="Please enter a valid amount")
                return
            for tithe in self.data["churches"][church_name]["tithes"]:
                if tithe.get("id", "")[:8] == tithe_id:
                    tithe["amount"] = amount
                    tithe["notes"] = notes_val
                    break
            self.save_data()
            self.populate_tree()
            self.status_label.config(text=f"Tithe updated for {member_name}")
            popup.destroy()

        def delete_tithe():
            self.data["churches"][church_name]["tithes"] = [
                t for t in self.data["churches"][church_name]["tithes"]
                if t.get("id", "")[:8] != tithe_id
            ]
            self.save_data()
            self.populate_tree()
            self.status_label.config(text=f"The deleted for {member_name}")
            popup.destroy()

        tk.Button(
            btn_frame,
            text="Save Changes",
            bg=self.colors["button"],
            fg=self.colors["button_fg"],
            command=save_edit,
            relief=tk.FLAT,
            padx=20,
            pady=5,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Delete Tithe",
            bg="#d94a4a",
            fg=self.colors["button_fg"],
            command=delete_tithe,
            relief=tk.FLAT,
            padx=20,
            pady=5,
        ).pack(side=tk.LEFT, padx=5)


def main():
    root = tk.Tk()
    app = TitherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
