# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def attest_via_tpm() -> bool:
    """
    Выполняет TPM-аттестацию:
    1) Проверяет наличие утилиты tpm2_quote.
    2) Читает все PCR-файлы из ZILANT_PCR_PATH (или по умолчанию /sys/class/tpm/tpm0/pcrs).
    3) Если PCR-каталог отсутствует или пуст, возвращает False.
    4) Генерирует команду tpm2_quote и сохраняет в ZILANT_QUOTE_FILE (по умолчанию /tmp/tpm_quote.bin).
    5) Если tpm2_quote не создал файл или вернул код != 0, возвращает False.
    6) Пытается верифицировать подпись через tpm2_verifysignature.
    7) Если верификация неуспешна (код != 0), возвращает False. В противном случае — True.
    """
    # 1) Проверяем, установлена ли утилита tpm2_quote
    if shutil.which("tpm2_quote") is None:
        return False

    # 2) Определяем PCR-каталог
    pcr_env = Path(os.environ.get("ZILANT_PCR_PATH", "/sys/class/tpm/tpm0/pcrs"))
    if not pcr_env.is_dir():
        return False

    # 3) Считываем все PCR-значения в словарь local_values[index] = data
    local_values: dict[int, bytes] = {}
    for entry in pcr_env.iterdir():
        try:
            idx = int(entry.name)
            data = entry.read_bytes().strip()
            local_values[idx] = data
        except Exception:
            continue
    if not local_values:
        return False

    # 4) Формируем путь до файла с квотой
    quote_file = Path(os.environ.get("ZILANT_QUOTE_FILE", "/tmp/tpm_quote.bin"))
    # Список индексов PCR для передачи в tpm2_quote
    pcr_list = ",".join(str(i) for i in sorted(local_values.keys()))
    cmd_quote = [
        "tpm2_quote",
        "-C",
        os.environ.get("ZILANT_TPM_KEY_CTX", "0x81010001"),
        "-l",
        pcr_list,
        "-q",
        str(quote_file),
    ]
    # Запускаем tpm2_quote
    result = subprocess.run(cmd_quote, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # 5) Если код возврата != 0 или файл не создан — отказываем
    if result.returncode != 0 or not quote_file.exists():
        return False

    # 6) Формируем команду для проверки подписи
    sig_file = f"{quote_file}.sig"
    cmd_verify = [
        "tpm2_verifysignature",
        "-c",
        os.environ.get("ZILANT_TPM_PUBKEY_CTX", "0x81010002"),
        "-m",
        str(quote_file),
        "-s",
        sig_file,
    ]
    result_verify = subprocess.run(cmd_verify, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # 7) Возвращаем успешность верификации (True/False)
    return result_verify.returncode == 0
