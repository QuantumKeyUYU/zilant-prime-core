from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QLabel, QProgressBar, QPushButton, QVBoxLayout, QWidget


class Window(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Zilant GUI")
        self.setAcceptDrops(True)
        self._file: Path | None = None

        self.label = QLabel("Drop file to pack")
        self.label.setAlignment(Qt.AlignCenter)

        self.pack_btn = QPushButton("Pack")
        self.pack_btn.clicked.connect(self.pack)
        self.unpack_btn = QPushButton("Unpack")
        self.unpack_btn.clicked.connect(self.unpack)
        self.sbom_btn = QPushButton("Generate SBOM")
        self.sbom_btn.clicked.connect(self.gen_sbom)

        self.progress = QProgressBar()
        self.progress.setVisible(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.pack_btn)
        layout.addWidget(self.unpack_btn)
        layout.addWidget(self.sbom_btn)
        layout.addWidget(self.progress)

    def dragEnterEvent(self, event):  # type: ignore[override]
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):  # type: ignore[override]
        urls = event.mimeData().urls()
        if urls:
            self._file = Path(urls[0].toLocalFile())
            self.label.setText(str(self._file))

    def _run(self, args: list[str]) -> None:
        self.progress.setVisible(True)
        try:
            subprocess.run(args, check=True)
        except Exception as exc:  # nosec - GUI surface
            self.label.setText(f"Error: {exc}")
        finally:
            self.progress.setVisible(False)

    def pack(self) -> None:
        if self._file:
            self._run(["zilant", "pack", str(self._file)])

    def unpack(self) -> None:
        if self._file:
            out = QFileDialog.getExistingDirectory(self, "Unpack to")
            if out:
                self._run(["zilant", "unpack", str(self._file), "-d", out])

    def gen_sbom(self) -> None:
        self._run(["syft", str(self._file or '.')])


def main() -> int:
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
