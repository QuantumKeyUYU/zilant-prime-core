import os, time, struct, tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from src.zil import create_zil, unpack_zil

class UYUBoxApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UYUBox")
        tk.Button(self, text="Pack",   command=self.pack_file).pack(pady=10)
        tk.Button(self, text="Unpack", command=self.unpack_file).pack(pady=10)

    def pack_file(self):
        inp = filedialog.askopenfilename(title="Select file to pack")
        if not inp: return
        pwd = simpledialog.askstring("Passphrase","Enter passphrase:",show="*")
        if pwd is None: return
        vdf_i = simpledialog.askinteger("VDF iters","Iterations:",initialvalue=100)
        tries = simpledialog.askinteger("Tries","Allowed tries:",initialvalue=1)
        meta = os.path.basename(inp)
        out = filedialog.asksaveasfilename(
            initialfile=meta + ".zil",
            defaultextension=".zil",
            filetypes=[("ZILANT","*.zil"),("All","*.*")],
            title="Save .zil as"
        )
        if not out: return
        blob = create_zil(open(inp,"rb").read(), pwd, vdf_i, tries, metadata=meta.encode())
        open(out,"wb").write(blob)
        messagebox.showinfo("UYUBox", f"✅ Packed:\n{out}")

    def unpack_file(self):
        inp = filedialog.askopenfilename(title="Select .zil to unpack", filetypes=[("ZILANT","*.zil")])
        if not inp: return
        pwd = simpledialog.askstring("Passphrase","Enter passphrase:",show="*")
        if pwd is None: return
        # распаковываем
        pt, meta = unpack_zil(open(inp,"rb").read(), pwd, metadata=b"")
        if pt is None:
            messagebox.showerror("UYUBox","❌ Wrong passphrase or self-destruct.")
            return

        # определяем имя и фильтр
        default = meta.decode() if meta else "output"
        ext = os.path.splitext(default)[1] or ""
        ftypes = [("All files","*.*")]
        out = filedialog.asksaveasfilename(
            initialfile=default,
            defaultextension=ext,
            filetypes=ftypes,
            title="Save output as"
        )
        if not out: return
        open(out,"wb").write(pt)
        messagebox.showinfo("UYUBox", f"✅ Unpacked:\n{out}")

if __name__ == "__main__":
    UYUBoxApp().mainloop()
