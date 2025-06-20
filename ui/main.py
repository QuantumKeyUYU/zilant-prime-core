#!/usr/bin/env python3
# ui/main.py

import subprocess
import sys
import threading
import time
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zilant Prime GUI")
        self.setAcceptDrops(True)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        central.setLayout(layout)

        self.label = QLabel("Перетащи файл сюда или выбери кнопкой")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

        self.btn_select = QPushButton("Выбрать файл...")
        self.btn_select.clicked.connect(self._select_file)
        layout.addWidget(self.btn_select)

        self.btn_pack = QPushButton("Pack")
        self.btn_pack.clicked.connect(lambda: self._run_task("pack"))
        self.btn_sbom = QPushButton("Generate SBOM")
        self.btn_sbom.clicked.connect(lambda: self._run_task("sbom"))
        layout.addWidget(self.btn_pack)
        layout.addWidget(self.btn_sbom)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self.label.setText(f"Файл: {path}")
            self._last_file = path

    def _select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if path:
            self.label.setText(f"Файл: {path}")
            self._last_file = path

    def _run_task(self, cmd):
        file_arg = getattr(self, "_last_file", None)
        args = ["zilant", cmd]
        if cmd == "pack" and file_arg:
            args.append(file_arg)

        self.progress.setValue(0)
        thread = threading.Thread(target=self._worker, args=(args,), daemon=True)
        thread.start()

    def _worker(self, args):
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        total = 100
        current = 0
        for _ in proc.stdout:
            current = min(current + total // 20, total)
            self.progress.setValue(current)
        proc.wait()
        self.progress.setValue(total)
        time.sleep(0.5)
        self.progress.setValue(0)


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(500, 300)
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
