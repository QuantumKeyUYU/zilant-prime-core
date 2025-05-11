import os

def strip_bom(file_path):
    with open(file_path, 'rb') as f:
        content = f.read()

    if content.startswith(b'\xef\xbb\xbf'):
        with open(file_path, 'wb') as f:
            f.write(content[3:])
        print(f"BOM removed from {file_path}")
    else:
        print(f"No BOM found in {file_path}")

if __name__ == "__main__":
    for root, _, files in os.walk("src"):
        for file in files:
            strip_bom(os.path.join(root, file))
