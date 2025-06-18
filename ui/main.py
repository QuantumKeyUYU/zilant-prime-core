from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class DropLabel(QLabel):
    def __init__(self, parent: "MainWindow") -> None:
        super().__init__("Drop file to pack/unpack")
        self._parent = parent
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):  # type: ignore[override]
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):  # type: ignore[override]
        urls = event.mimeData().urls()
        if urls:
            path = Path(urls[0].toLocalFile())
            self._parent.process_file(path)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Zilant GUI")
        self._file: Path | None = None

        self.drop_area = DropLabel(self)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.sbom_btn = QPushButton("Generate SBOM")
        self.sbom_btn.clicked.connect(self.gen_sbom)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.addWidget(self.drop_area)
        layout.addWidget(self.progress)
        layout.addWidget(self.sbom_btn)
        self.setCentralWidget(central)

        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction("Pack", self.pack)
        file_menu.addAction("Unpack", self.unpack)
        self.statusBar()

    # public API -----------------------------------------------------
    def process_file(self, path: Path) -> None:
        self._file = path
        self.drop_area.setText(str(path))
        if path.suffix == ".zil":
            self.unpack()
        else:
            self.pack()

    def pack(self) -> None:
        if not self._file:
            return
        self._run(["zilant", "pack", str(self._file)])

    def unpack(self) -> None:
        if not self._file:
            return
        out_dir = QFileDialog.getExistingDirectory(self, "Unpack to", str(self._file.parent))
        if out_dir:
            self._run(["zilant", "unpack", str(self._file), "-d", out_dir])

    def gen_sbom(self) -> None:
        target = str(self._file or ".")
        self._run(["zilant", "sbom", "--output", "sbom.json", target])
        QMessageBox.information(self, "SBOM", "sbom.json generated")

    # helpers --------------------------------------------------------
    def _run(self, args: list[str]) -> None:
        self.progress.setVisible(True)
        self.statusBar().showMessage("Running...")
        try:
            subprocess.run(args, check=True)
            self.statusBar().showMessage("Done", 5000)
        except Exception as exc:  # nosec - UI surface
            self.statusBar().showMessage(f"Error: {exc}", 5000)
        finally:
            self.progress.setVisible(False)


def main() -> int:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
