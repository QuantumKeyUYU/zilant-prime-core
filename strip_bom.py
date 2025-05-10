# strip_bom.py — запускается из корня проекта
import sys

F = "pyproject.toml"
data = open(F, "rb").read()
# BOM EF BB BF
if data.startswith(b"\xef\xbb\xbf"):
    data = data[3:]
    open(F, "wb").write(data)
    print("✔ BOM removed")
else:
    print("— no BOM found")
