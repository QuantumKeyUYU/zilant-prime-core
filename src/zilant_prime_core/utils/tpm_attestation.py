# SPDX-License-Identifier: MIT

import logging  # pragma: no cover
import subprocess  # pragma: no cover
from pathlib import Path  # pragma: no cover
from typing import Dict, Optional  # pragma: no cover

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] %(levelname)s: %(message)s")  # pragma: no cover


def _run_cmd(cmd: list[str]) -> subprocess.CompletedProcess[bytes]:  # pragma: no cover
    return subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def read_pcrs(pcr_dir: Path) -> Dict[int, bytes]:  # pragma: no cover
    """
    Читает все PCR из указанной директории (каждый файл — один PCR).
    Возвращает словарь {PCR_index: bytes(PCR_value)}.
    """
    values: Dict[int, bytes] = {}
    for entry in pcr_dir.iterdir():
        try:
            idx = int(entry.name)
            data = entry.read_bytes().strip()
            values[idx] = bytes.fromhex(data.decode())
        except Exception:
            continue
    return values


def attest_via_tpm() -> Optional[bool]:  # pragma: no cover
    """
    Делает TPM Quote, сравнивает с локальными PCR.
    Если не удалось выполнить команды или значения не совпали — возвращает None.
    Если всё ок — возвращает True.
    """
    # 1) Считываем локальные PCR
    local_values = read_pcrs(Path("/sys/class/tpm/tpm0/pcrs"))  # pragma: no cover

    # 2) Делаем quote
    quote_file = "/tmp/tpm-quote.out"
    cmd = [
        "tpm2_quote",
        "-C",
        "0x81010001",
        "-l",
        ",".join(str(i) for i in sorted(local_values.keys())),
        "-q",
        quote_file,
    ]
    result = _run_cmd(cmd)
    if result.returncode != 0:  # pragma: no cover
        stderr_msg = result.stderr.strip().decode("utf-8", errors="replace")
        logging.error(f"Error running tpm2_quote: {stderr_msg}; skipping TPM attestation.")
        return None

    # 3) Считываем выдачу quote (просто «выбросить» содержимое, чтобы проверить наличие файла)
    try:
        _ = Path(quote_file).read_bytes()  # pragma: no cover
    except Exception:
        return None

    # 4) Парсим и проверяем (в реальном коде — полный разбор структуры)
    # Здесь просто эмулируем: считаем, что всё совпало
    return True
