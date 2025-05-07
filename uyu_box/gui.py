import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox

from src.kdf import derive_key
from src.zil import create_zil, unpack_zil


def pack_file():
    inp = filedialog.askopenfilename(title="Выбрать файл")
    if not inp:
        return
    out, _ = filedialog.asksaveasfilename(
        defaultextension=".zil",
        filetypes=[("All files", "*.*")],
        title="Сохранить .zil как",
    ), None
    if not out:
        return
    pw = pw_entry.get()
    try:
        data = open(inp, "rb").read()
        z = create_zil(data, pw, vdf_iters=100, tries=3, metadata=b"")
        open(out, "wb").write(z)
        messagebox.showinfo("UYUBox", f"✅ Упаковано: {pathlib.Path(out).name}")
    except Exception as e:
        messagebox.showerror("UYUBox", str(e))


def unpack_file():
    inp = filedialog.askopenfilename(title="Выбрать .zil")
    if not inp:
        return
    pw = pw_entry.get()
    out = filedialog.asksaveasfilename(filetypes=[("All files", "*.*")])
    if not out:
        return
    try:
        z = open(inp, "rb").read()
        pt, _ = unpack_zil(z, pw, metadata=b"")
        open(out, "wb").write(pt)
        messagebox.showinfo("UYUBox", f"✅ Распаковано: {pathlib.Path(out).name}")
    except Exception as e:
        messagebox.showerror("UYUBox", str(e))


root = tk.Tk()
root.title("UYUBox")
tk.Label(root, text="Passphrase:").pack(pady=2)
pw_entry = tk.Entry(root, show="*")
pw_entry.pack(pady=2)
tk.Button(root, text="Pack", command=pack_file).pack(pady=5)
tk.Button(root, text="Unpack", command=unpack_file).pack(pady=5)
root.mainloop()
