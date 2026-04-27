import tkinter as tk
from tkinter import messagebox
import json, os
from datetime import datetime

DATA = "tasks.json"

def load():
    if os.path.exists(DATA):
        with open(DATA) as f:
            return json.load(f)
    return []

def save(t):
    with open(DATA, "w") as f:
        json.dump(t, f, indent=2)

tasks = load()

BG      = "#0d0d0f"
PANEL   = "#13131a"
CARD    = "#1c1c26"
CARD_H  = "#22222e"
DONE_BG = "#161620"
ACC     = "#7c6bff"
ACC2    = "#a594ff"
GREEN   = "#4ade80"
RED     = "#f87171"
TEXT    = "#f0f0ff"
SUB     = "#7070a0"
MUTED   = "#3a3a55"
BORDER  = "#2a2a3a"
WHITE   = "#ffffff"

CATS = {
    "work":     ("#38bdf8", "#0d2030"),
    "personal": ("#a594ff", "#1a1030"),
    "urgent":   ("#f87171", "#2a0f0f"),
    "idea":     ("#4ade80", "#0a2015"),
    "none":     (MUTED,     CARD),
}

root = tk.Tk()
root.title("tasks.")
root.geometry("560x800")
root.configure(bg=BG)
root.resizable(False, False)

try:
    root.tk.call("tk", "scaling", 1.25)
except:
    pass

filter_var = tk.StringVar(value="all")
cat_var    = tk.StringVar(value="none")
cat_btns   = {}

def render():
    for w in scroll_inner.winfo_children():
        w.destroy()

    filt  = filter_var.get()
    shown = [(i, t) for i, t in enumerate(tasks)
             if filt == "all"
             or (filt == "open" and not t["done"])
             or (filt == "done" and t["done"])]

    if not shown:
        _empty_state()
    else:
        for idx, task in shown:
            _make_card(scroll_inner, task, idx)

    _update_progress()
    scroll_inner.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

def _empty_state():
    f = tk.Frame(scroll_inner, bg=BG)
    f.pack(expand=True, pady=70)
    tk.Label(f, text="✦  ◈  ⬡", font=("Helvetica", 11),
             bg=BG, fg=MUTED).pack()
    tk.Label(f, text="nothing here yet", font=("Helvetica", 15, "italic"),
             bg=BG, fg=SUB).pack(pady=(12, 4))
    tk.Label(f, text="add something above ↑", font=("Helvetica", 9),
             bg=BG, fg=MUTED).pack()

def _make_card(parent, task, idx):
    done = task["done"]
    cat  = task.get("cat", "none") or "none"
    cfg, cbg2 = CATS.get(cat, CATS["none"])
    card_bg = DONE_BG if done else CARD

    outer = tk.Frame(parent, bg=BG)
    outer.pack(fill="x", padx=16, pady=5)

    shadow = tk.Frame(outer, bg="#09090e", height=4)
    shadow.pack(fill="x", padx=6)

    card = tk.Frame(outer, bg=card_bg, pady=14)
    card.pack(fill="x")

    stripe = tk.Frame(card, bg=cfg, width=4)
    stripe.pack(side="left", fill="y", padx=(10, 0))

    body = tk.Frame(card, bg=card_bg, padx=14)
    body.pack(side="left", fill="both", expand=True)

    row1 = tk.Frame(body, bg=card_bg)
    row1.pack(fill="x")

    chk_bg  = cfg if done else MUTED
    chk_txt = "✓" if done else " "

    chk_wrap = tk.Frame(row1, bg=chk_bg, width=22, height=22)
    chk_wrap.pack(side="left", padx=(0, 10))
    chk_wrap.pack_propagate(False)

    chk = tk.Label(chk_wrap, text=chk_txt, font=("Helvetica", 9, "bold"),
                   bg=chk_bg, fg=BG)
    chk.place(relx=.5, rely=.5, anchor="center")

    for w in [chk_wrap, chk]:
        w.bind("<Button-1>", lambda e, i=idx: toggle(i))
        w.config(cursor="hand2")

    tfont = ("Helvetica", 12, "overstrike") if done else ("Helvetica", 12, "bold")
    tcol  = SUB if done else TEXT
    title_lbl = tk.Label(row1, text=task["title"], font=tfont, bg=card_bg,
                         fg=tcol, anchor="w", wraplength=340, justify="left")
    title_lbl.pack(side="left", fill="x", expand=True)

    del_lbl = tk.Label(row1, text="⊗", font=("Helvetica", 15),
                       bg=card_bg, fg=MUTED, cursor="hand2", padx=4)
    del_lbl.pack(side="right")
    del_lbl.bind("<Button-1>", lambda e, i=idx: delete(i))
    del_lbl.bind("<Enter>",    lambda e: del_lbl.config(fg=RED))
    del_lbl.bind("<Leave>",    lambda e: del_lbl.config(fg=MUTED))

    if task.get("note"):
        tk.Label(body, text=task["note"], font=("Helvetica", 9, "italic"),
                 bg=card_bg, fg=SUB, anchor="w",
                 wraplength=350, justify="left", pady=4).pack(fill="x")

    meta = tk.Frame(body, bg=card_bg)
    meta.pack(fill="x", pady=(6, 0))

    if cat != "none":
        fg2, bg2 = CATS[cat]
        tk.Label(meta, text=f"  {cat}  ", font=("Helvetica", 8, "bold"),
                 bg=bg2, fg=fg2, pady=2).pack(side="left", padx=(0, 6))

    ts = task.get("ts", "")
    if ts:
        tk.Label(meta, text=ts, font=("Helvetica", 8),
                 bg=card_bg, fg=MUTED).pack(side="right")

    hover_in  = lambda e, c=card, b=card_bg: c.config(bg=CARD_H if not done else b)
    hover_out = lambda e, c=card, b=card_bg: c.config(bg=b)
    for w in [card, body, row1, meta]:
        w.bind("<Enter>", hover_in)
        w.bind("<Leave>", hover_out)

def _update_progress():
    total = len(tasks)
    done  = sum(1 for t in tasks if t["done"])
    pct   = done / total if total else 0

    count_lbl.config(text=f"{total - done} open  ·  {done} done  ·  {total} total")

    pw = 500
    prog_canvas.delete("all")
    prog_canvas.create_rectangle(0, 1, pw, 7, fill=MUTED, outline="", width=0)
    if pct > 0:
        prog_canvas.create_rectangle(0, 1, int(pw * pct), 7,
                                     fill=ACC, outline="", width=0)
    pct_lbl.config(text=f"{int(pct * 100)}%")

def toggle(idx):
    tasks[idx]["done"] = not tasks[idx]["done"]
    save(tasks)
    render()

def delete(idx):
    name = tasks[idx]["title"]
    if messagebox.askyesno("delete?", f'remove "{name}"?',
                           icon="warning", parent=root):
        tasks.pop(idx)
        save(tasks)
        render()

def add_task():
    title = entry.get().strip()
    if not title:
        entry.config(highlightbackground=RED, highlightcolor=RED)
        root.after(700, lambda: entry.config(
            highlightbackground=BORDER, highlightcolor=ACC))
        return
    note = note_box.get("1.0", "end").strip()
    cat  = cat_var.get()
    tasks.insert(0, {
        "title": title,
        "note":  note,
        "cat":   cat if cat != "none" else "",
        "done":  False,
        "ts":    datetime.now().strftime("%b %d, %H:%M"),
    })
    save(tasks)
    entry.delete(0, tk.END)
    note_box.delete("1.0", tk.END)
    cat_var.set("none")
    _refresh_cats()
    render()
    entry.focus()

def clear_done():
    global tasks
    n = sum(1 for t in tasks if t["done"])
    if not n:
        return
    if messagebox.askyesno("clear?",
                           f"remove {n} completed task{'s' if n > 1 else ''}?",
                           parent=root):
        tasks = [t for t in tasks if not t["done"]]
        save(tasks)
        render()

def _select_cat(cat):
    cat_var.set(cat)
    _refresh_cats()

def _refresh_cats():
    sel = cat_var.get()
    for cat, btn in cat_btns.items():
        fg, _ = CATS.get(cat, (MUTED, CARD))
        if cat == sel:
            btn.config(bg=fg, fg=BG)
        else:
            btn.config(bg=CARD, fg=fg)

root.columnconfigure(0, weight=1)

header = tk.Frame(root, bg=BG, pady=22, padx=24)
header.pack(fill="x")

h_top = tk.Frame(header, bg=BG)
h_top.pack(fill="x")

title_row = tk.Frame(h_top, bg=BG)
title_row.pack(side="left")
tk.Label(title_row, text="tasks.", font=("Helvetica", 30, "bold"),
         bg=BG, fg=WHITE).pack(side="left")
tk.Label(title_row, text="  ⬡", font=("Helvetica", 17),
         bg=BG, fg=ACC).pack(side="left", pady=(8, 0))

clr = tk.Label(h_top, text="clear done", font=("Helvetica", 9),
               bg=BG, fg=SUB, cursor="hand2")
clr.pack(side="right", pady=(12, 0))
clr.bind("<Button-1>", lambda e: clear_done())
clr.bind("<Enter>",    lambda e: clr.config(fg=RED))
clr.bind("<Leave>",    lambda e: clr.config(fg=SUB))

count_lbl = tk.Label(header, text="", font=("Helvetica", 9),
                     bg=BG, fg=SUB)
count_lbl.pack(anchor="w", pady=(4, 10))

prog_row = tk.Frame(header, bg=BG)
prog_row.pack(fill="x")

prog_canvas = tk.Canvas(prog_row, bg=BG, height=8, width=500,
                        highlightthickness=0)
prog_canvas.pack(side="left")

pct_lbl = tk.Label(prog_row, text="0%", font=("Helvetica", 8, "bold"),
                   bg=BG, fg=ACC)
pct_lbl.pack(side="right", padx=(8, 0))

panel = tk.Frame(root, bg=PANEL, pady=18, padx=18)
panel.pack(fill="x", padx=14, pady=(0, 6))

tk.Label(panel, text="NEW TASK", font=("Helvetica", 8, "bold"),
         bg=PANEL, fg=MUTED).pack(anchor="w", pady=(0, 5))

entry = tk.Entry(panel, font=("Helvetica", 13, "bold"), bg=CARD, fg=TEXT,
                 insertbackground=ACC2, relief="flat", bd=0,
                 highlightthickness=2, highlightbackground=BORDER,
                 highlightcolor=ACC)
entry.pack(fill="x", ipady=10)
entry.bind("<FocusIn>",  lambda e: entry.config(highlightbackground=ACC))
entry.bind("<FocusOut>", lambda e: entry.config(highlightbackground=BORDER))
entry.bind("<Return>", lambda e: add_task())
entry.focus()

tk.Frame(panel, bg=PANEL, height=10).pack()

note_hdr = tk.Frame(panel, bg=PANEL)
note_hdr.pack(fill="x")
tk.Label(note_hdr, text="NOTE", font=("Helvetica", 8, "bold"),
         bg=PANEL, fg=MUTED).pack(side="left")
tk.Label(note_hdr, text="  optional", font=("Helvetica", 8),
         bg=PANEL, fg=MUTED).pack(side="left")

note_box = tk.Text(panel, font=("Helvetica", 10), bg=CARD, fg=SUB,
                   insertbackground=ACC2, relief="flat", bd=0,
                   highlightthickness=2, highlightbackground=BORDER,
                   highlightcolor=ACC, height=2, wrap="word")
note_box.pack(fill="x", pady=(5, 0))
note_box.bind("<FocusIn>",  lambda e: note_box.config(
    highlightbackground=ACC, fg=TEXT))
note_box.bind("<FocusOut>", lambda e: note_box.config(
    highlightbackground=BORDER, fg=SUB))

tk.Frame(panel, bg=PANEL, height=10).pack()

tk.Label(panel, text="CATEGORY", font=("Helvetica", 8, "bold"),
         bg=PANEL, fg=MUTED).pack(anchor="w", pady=(0, 6))

cat_row = tk.Frame(panel, bg=PANEL)
cat_row.pack(fill="x")

for cat in ["none", "work", "personal", "urgent", "idea"]:
    fg, _ = CATS.get(cat, (MUTED, CARD))
    label = "—" if cat == "none" else cat
    b = tk.Label(cat_row, text=f"  {label}  ",
                 font=("Helvetica", 9, "bold"),
                 bg=CARD, fg=fg, cursor="hand2",
                 padx=4, pady=5)
    b.pack(side="left", padx=(0, 5))
    b.bind("<Button-1>", lambda e, c=cat: _select_cat(c))
    cat_btns[cat] = b

_refresh_cats()

tk.Frame(panel, bg=PANEL, height=12).pack()

add_btn = tk.Button(panel, text="＋  add task",
                    font=("Helvetica", 11, "bold"),
                    bg=ACC, fg=WHITE, relief="flat", bd=0,
                    activebackground=ACC2, activeforeground=WHITE,
                    cursor="hand2", pady=9, command=add_task)
add_btn.pack(fill="x")
add_btn.bind("<Enter>", lambda e: add_btn.config(bg=ACC2))
add_btn.bind("<Leave>", lambda e: add_btn.config(bg=ACC))

fbar = tk.Frame(root, bg=BG, pady=8, padx=14)
fbar.pack(fill="x")

for lbl, val in [("all", "all"), ("open ○", "open"), ("done ✓", "done")]:
    rb = tk.Radiobutton(fbar, text=lbl, variable=filter_var, value=val,
                        font=("Helvetica", 9, "bold"),
                        bg=BG, fg=SUB, selectcolor=BG,
                        activebackground=BG, activeforeground=ACC,
                        indicatoron=False, relief="flat", bd=0,
                        padx=12, pady=5, highlightthickness=0,
                        command=render)
    rb.pack(side="left", padx=2)

divider = tk.Frame(root, bg=BORDER, height=1)
divider.pack(fill="x", padx=14)

list_wrap = tk.Frame(root, bg=BG)
list_wrap.pack(fill="both", expand=True)

canvas = tk.Canvas(list_wrap, bg=BG, highlightthickness=0, bd=0)
scrollbar = tk.Scrollbar(list_wrap, orient="vertical",
                         command=canvas.yview,
                         bg=BG, troughcolor=BG,
                         activebackground=MUTED, width=6)
canvas.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

scroll_inner = tk.Frame(canvas, bg=BG)
win_id = canvas.create_window((0, 0), window=scroll_inner, anchor="nw")

canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(win_id, width=e.width))
canvas.bind_all("<MouseWheel>",
                lambda e: canvas.yview_scroll(
                    int(-1 * (e.delta / 120)), "units"))

status = tk.Frame(root, bg=PANEL, pady=7, padx=16)
status.pack(fill="x", side="bottom")
tk.Label(status,
         text="↵ to add  ·  click checkbox to complete  ·  ⊗ to delete",
         font=("Helvetica", 8), bg=PANEL, fg=MUTED).pack()

render()
root.mainloop()