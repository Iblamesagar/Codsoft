import tkinter as tk
from tkinter import messagebox, simpledialog
import json, os, re

DATA = os.path.join(os.path.dirname(__file__), "contacts_data.json")

BG      = "#111111"
SIDE    = "#1a1a1a"
CARD    = "#1e1e1e"
ACCENT  = "#7c5cbf"
ACCENT2 = "#9b7de8"
TEXT    = "#e8e8e8"
MUTED   = "#888888"
BORDER  = "#2a2a2a"
GREEN   = "#4ade80"
RED     = "#f87171"
INPUT   = "#252525"

def load():
    if os.path.exists(DATA):
        with open(DATA) as f:
            return json.load(f)
    return []

def save(contacts):
    with open(DATA, "w") as f:
        json.dump(contacts, f, indent=2)

def initials(name):
    parts = name.strip().split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return name[:2].upper() if name else "??"

COLORS = ["#7c5cbf","#5b8dd9","#d97b5b","#5bbd8e","#d9a35b","#bd5b8e"]

def avatar_color(name):
    return COLORS[sum(ord(c) for c in name) % len(COLORS)]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("contacts")
        self.geometry("820x560")
        self.minsize(700, 480)
        self.configure(bg=BG)
        self.contacts = load()
        self.selected = None
        self.build()

    def build(self):
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        left = tk.Frame(self, bg=SIDE, width=240)
        left.grid(row=0, column=0, sticky="nsew")
        left.pack_propagate(False)
        left.grid_propagate(False)

        top_bar = tk.Frame(left, bg=SIDE, pady=14, padx=14)
        top_bar.pack(fill="x")

        hdr = tk.Frame(top_bar, bg=SIDE)
        hdr.pack(fill="x", pady=(0,10))
        self.count_var = tk.StringVar()
        tk.Label(hdr, text="CONTACTS", bg=SIDE, fg=TEXT,
                 font=("Courier", 10, "bold"), anchor="w").pack(side="left")
        tk.Label(hdr, textvariable=self.count_var, bg=SIDE, fg=ACCENT2,
                 font=("Courier", 10)).pack(side="left", padx=6)

        search_frame = tk.Frame(top_bar, bg=BORDER, bd=0)
        search_frame.pack(fill="x")
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *_: self.refresh_list())
        tk.Entry(search_frame, textvariable=self.search_var,
                 bg=INPUT, fg=MUTED, insertbackground=TEXT,
                 relief="flat", font=("Courier", 10),
                 bd=6).pack(fill="x")

        # list
        list_wrap = tk.Frame(left, bg=SIDE)
        list_wrap.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(list_wrap, bg=SIDE, highlightthickness=0, bd=0)
        sb = tk.Scrollbar(list_wrap, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.list_inner = tk.Frame(self.canvas, bg=SIDE)
        self.canvas_win = self.canvas.create_window((0,0), window=self.list_inner, anchor="nw")
        self.list_inner.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(
            self.canvas_win, width=e.width))

        # add button
        add_btn = tk.Frame(left, bg=ACCENT, cursor="hand2")
        add_btn.pack(fill="x", side="bottom")
        tk.Label(add_btn, text="+ add contact", bg=ACCENT, fg=TEXT,
                 font=("Courier", 10, "bold"), pady=12).pack()
        add_btn.bind("<Button-1>", lambda e: self.open_form())
        for w in add_btn.winfo_children():
            w.bind("<Button-1>", lambda e: self.open_form())


        self.right = tk.Frame(self, bg=BG)
        self.right.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)

        self.show_placeholder()
        self.refresh_list()

    def show_placeholder(self):
        for w in self.right.winfo_children():
            w.destroy()
        wrap = tk.Frame(self.right, bg=BG)
        wrap.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(wrap, text="◉", bg=BG, fg="#333", font=("Courier", 36)).pack()
        tk.Label(wrap, text="select a contact", bg=BG, fg=MUTED,
                 font=("Courier", 11)).pack(pady=4)

    def refresh_list(self):
        for w in self.list_inner.winfo_children():
            w.destroy()
        q = self.search_var.get().lower()
        items = [c for c in self.contacts if q in c["name"].lower() or q in c["phone"]]
        self.count_var.set(str(len(items)))
        for c in items:
            self.make_row(c)

    def make_row(self, c):
        row = tk.Frame(self.list_inner, bg=SIDE, cursor="hand2")
        row.pack(fill="x")

        sep = tk.Frame(row, bg=BORDER, height=1)
        sep.pack(fill="x")

        inner = tk.Frame(row, bg=SIDE, pady=10, padx=12)
        inner.pack(fill="x")

        av = tk.Label(inner, text=initials(c["name"]),
                      bg=avatar_color(c["name"]), fg="white",
                      font=("Courier", 10, "bold"),
                      width=3, height=1, relief="flat")
        av.pack(side="left", padx=(0,10))

        info = tk.Frame(inner, bg=SIDE)
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=c["name"], bg=SIDE, fg=TEXT,
                 font=("Courier", 10, "bold"), anchor="w").pack(fill="x")
        tk.Label(info, text=c["phone"], bg=SIDE, fg=MUTED,
                 font=("Courier", 9), anchor="w").pack(fill="x")

        def click(e, contact=c):
            self.selected = contact
            self.show_detail(contact)

        for w in [row, inner, av, info] + list(info.winfo_children()):
            w.bind("<Button-1>", click)

        def hover_on(e, r=row, i=inner):
            r.config(bg="#232323"); i.config(bg="#232323")
        def hover_off(e, r=row, i=inner):
            r.config(bg=SIDE); i.config(bg=SIDE)

        row.bind("<Enter>", hover_on)
        row.bind("<Leave>", hover_off)

    def show_detail(self, c):
        for w in self.right.winfo_children():
            w.destroy()

        wrap = tk.Frame(self.right, bg=BG)
        wrap.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85)

        # avatar big
        av_color = avatar_color(c["name"])
        av = tk.Label(wrap, text=initials(c["name"]),
                      bg=av_color, fg="white",
                      font=("Courier", 22, "bold"),
                      width=3, height=1)
        av.pack(pady=(0,14))

        tk.Label(wrap, text=c["name"], bg=BG, fg=TEXT,
                 font=("Courier", 18, "bold")).pack()
        tk.Label(wrap, text=c["phone"], bg=BG, fg=MUTED,
                 font=("Courier", 11)).pack(pady=2)

        # fields
        fields_frame = tk.Frame(wrap, bg=CARD, pady=14, padx=18)
        fields_frame.pack(fill="x", pady=20)

        def field_row(label, val):
            r = tk.Frame(fields_frame, bg=CARD)
            r.pack(fill="x", pady=5)
            tk.Label(r, text=label, bg=CARD, fg=MUTED,
                     font=("Courier", 8), anchor="w", width=8).pack(side="left")
            tk.Label(r, text=val or "—", bg=CARD, fg=TEXT,
                     font=("Courier", 10), anchor="w").pack(side="left")

        field_row("phone", c["phone"])
        field_row("email", c.get("email",""))
        field_row("addr", c.get("address",""))

        # buttons
        btn_row = tk.Frame(wrap, bg=BG)
        btn_row.pack()

        def styled_btn(parent, label, color, cmd):
            b = tk.Label(parent, text=label, bg=color, fg=TEXT,
                         font=("Courier", 9, "bold"),
                         padx=16, pady=7, cursor="hand2")
            b.pack(side="left", padx=6)
            b.bind("<Button-1>", lambda e: cmd())
            return b

        styled_btn(btn_row, "edit", ACCENT, lambda: self.open_form(c))
        styled_btn(btn_row, "delete", "#5a2626", lambda: self.delete_contact(c))

    def open_form(self, contact=None):
        win = tk.Toplevel(self)
        win.title("edit" if contact else "new contact")
        win.geometry("400x440")
        win.configure(bg=BG)
        win.grab_set()

        tk.Label(win, text="edit contact" if contact else "new contact",
                 bg=BG, fg=TEXT, font=("Courier", 14, "bold")).pack(pady=(18,12))

        fields = {}
        for label, key in [("name","name"),("phone","phone"),("email","email"),("address","address")]:
            row = tk.Frame(win, bg=BG)
            row.pack(fill="x", padx=30, pady=5)
            tk.Label(row, text=label, bg=BG, fg=MUTED,
                     font=("Courier", 9), anchor="w").pack(fill="x")
            var = tk.StringVar(value=contact.get(key,"") if contact else "")
            e = tk.Entry(row, textvariable=var, bg=INPUT, fg=TEXT,
                         insertbackground=TEXT, relief="flat",
                         font=("Courier", 11), bd=6)
            e.pack(fill="x")
            fields[key] = var

        def submit():
            name = fields["name"].get().strip()
            phone = fields["phone"].get().strip()
            if not name or not phone:
                messagebox.showwarning("oops", "name and phone are required", parent=win)
                return
            data = {k: v.get().strip() for k,v in fields.items()}
            if contact:
                idx = self.contacts.index(contact)
                self.contacts[idx] = data
                self.selected = data
            else:
                self.contacts.append(data)
            save(self.contacts)
            self.refresh_list()
            if contact:
                self.show_detail(data)
            else:
                self.show_placeholder()
            win.destroy()

        tk.Frame(win, bg=BG, height=10).pack()
        save_btn = tk.Label(win, text="save", bg=ACCENT, fg=TEXT,
                            font=("Courier", 11, "bold"),
                            pady=10, cursor="hand2")
        save_btn.pack(fill="x", padx=30)
        save_btn.bind("<Button-1>", lambda e: submit())

    def delete_contact(self, c):
        if messagebox.askyesno("delete?", f"remove {c['name']}?"):
            self.contacts.remove(c)
            save(self.contacts)
            self.refresh_list()
            self.show_placeholder()


if __name__ == "__main__":
    App().mainloop()