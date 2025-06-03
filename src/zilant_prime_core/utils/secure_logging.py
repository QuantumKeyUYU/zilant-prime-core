# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import base64
import json
import os
import secrets
from typing import Any, Optional, Tuple, Union

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

__all__ = ["SecureLogger", "get_secure_logger"]


class SecureLogger:
    """Логгер с AES-GCM, защитой от log-injection и JSON-обёрткой."""

    def __init__(self, key: Optional[bytes] = None, log_path: str = "secure.log") -> None:
        raw: Optional[bytes] = key or os.environ.get("ZILANT_LOG_KEY")  # type: ignore[assignment]
        if isinstance(raw, str):
            raw = base64.urlsafe_b64decode(raw.encode())
        if not isinstance(raw, (bytes, bytearray)) or len(raw) != 32:
            raise ValueError("Log key must be 32 bytes")
        self._aesgcm = AESGCM(raw)
        self.log_path = log_path

    def _sanitize(self, msg: str) -> str:
        """
        Экранируем управляющие символы (\n, \r) и удаляем всё, что вне диапазона ASCII 32–126.
        Это защищает от log-injection.
        """
        # Заменяем любые реальные \n и \r
        escaped = msg.replace("\n", "\\n").replace("\r", "\\r")
        # Оставляем только символы из диапазона 32..126 (печатаемые ASCII)
        return "".join(ch for ch in escaped if 32 <= ord(ch) < 127)

    def log(self, msg: str, level: str = "INFO", **fields: Any) -> None:
        """
        Записывает зашифрованную запись в файл.

        Перед шифрованием формируется JSON-объект:
          {
            "msg": <санитизированный msg>,
            "level": <уровень>,
            # любые дополнительные ключи: значения из **fields
          }

        Затем JSON кодируется UTF-8, шифруется AES-GCM,
        и в файл добавляется строка:
          base64(nonce) | base64(ciphertext)\n

        Параметры:
          msg (str): исходный текст сообщения
          level (str): уровень логирования ("INFO", "ERROR" и т. д.)
          **fields: любые дополнительные поля (ключ-значение).
                    Если тип значения не один из (str, int, float, bool, None),
                    он приводится к строке через str().
        """
        sanitized = self._sanitize(msg)
        record_dict: dict[str, Any] = {"msg": sanitized, "level": level}

        # Включаем дополнительные поля, если они переданы
        if fields:
            for key, value in fields.items():
                # Разрешаем только «примитивные» типы напрямую,
                # всё остальное конвертируем в строку
                if isinstance(value, (str, int, float, bool)) or value is None:
                    record_dict[key] = value
                else:
                    record_dict[key] = str(value)

        # Сериализуем JSON компактно (без пробелов)
        record = json.dumps(record_dict, separators=(",", ":"))
        nonce = secrets.token_bytes(12)
        ct = self._aesgcm.encrypt(nonce, record.encode("utf-8"), None)

        # Собираем строку в файле: base64(nonce) | base64(ciphertext)
        entry = b"|".join(
            [
                base64.b64encode(nonce),
                base64.b64encode(ct),
            ]
        )

        # Гарантируем, что папка для лога существует
        directory = os.path.dirname(self.log_path) or "."
        os.makedirs(directory, exist_ok=True)

        # Дописываем в файл одну строку
        with open(self.log_path, "ab") as f:
            f.write(entry + b"\n")

    def read_logs(self) -> list[Union[Tuple[str, str], Tuple[str, str, dict[str, Any]]]]:
        """
        Читает все зашифрованные строки из файла, расшифровывает их и возвращает список:
          - (level, msg) для каждой записи (даже если есть доп. поля),
          - а затем, если были доп. поля, ещё (level, msg, {…}) для той же записи.

        Если файл не найден, возвращает [] без ошибок.

        Алгоритм:
          1) Если файл отсутствует, вернуть [].
          2) Иначе открыть файл в бинарном режиме.
          3) Для каждой строки:
             a) Разбиваем по разделителю '|' -> [nonce_b64, ct_b64]
             b) Декодируем base64, расшифровываем AES-GCM -> JSON-строка
             c) Парсим JSON -> dict payload
             d) Извлекаем обязательные поля:
                lvl = payload.pop("level")
                msg = payload.pop("msg")
             e) Оставшиеся ключи (если есть) – это доп. поля
             f) Всегда добавляем сначала (lvl, msg) в результирующий список.
             g) Если доп. поля есть, добавляем ещё (lvl, msg, remaining_fields).
        """
        out: list[Union[Tuple[str, str], Tuple[str, str, dict[str, Any]]]] = []

        # Если файл лога не существует, сразу возвращаем пустой список
        if not os.path.exists(self.log_path):
            return out  # pragma: no cover

        with open(self.log_path, "rb") as f:
            for line in f:
                parts = line.rstrip(b"\n").split(b"|")
                if len(parts) != 2:
                    # Если строка не в том формате, пропускаем
                    continue

                n_b64, ct_b64 = parts
                try:
                    nonce = base64.b64decode(n_b64)
                    ct = base64.b64decode(ct_b64)
                except Exception:
                    # Некорректное base64 — пропускаем
                    continue

                try:
                    raw = self._aesgcm.decrypt(nonce, ct, None)
                except Exception:
                    # Если аутентификация не прошла, пропускаем запись
                    continue

                try:
                    payload = json.loads(raw.decode("utf-8"))
                except Exception:
                    # Если JSON некорректен, пропускаем запись
                    continue

                lvl = payload.pop("level", "")
                msg = payload.pop("msg", "")
                remaining_fields = {k: v for k, v in payload.items()}

                # Всегда добавляем кортеж (lvl, msg)
                out.append((lvl, msg))

                # Если есть доп. поля, добавляем ещё трёхэлементный кортеж
                if remaining_fields:
                    out.append((lvl, msg, remaining_fields))

        return out


_default: Optional[SecureLogger] = None


def get_secure_logger(key: Optional[bytes] = None, log_path: str = "secure.log") -> SecureLogger:
    """
    Возвращает Singleton SecureLogger.
    При первом вызове, если:
      - key не передан, и
      - в окружении нет ZILANT_LOG_KEY,
    то генерируется рандомный 32-байтовый ключ и сохраняется в ZILANT_LOG_KEY (base64).

    Дальше создаётся один экземпляр SecureLogger(key, log_path) и запоминается
    в глобальной переменной _default. Повторные вызовы возвращают уже его.
    """
    global _default
    if _default is None:
        if key is None and "ZILANT_LOG_KEY" not in os.environ:
            os.environ["ZILANT_LOG_KEY"] = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode()
        _default = SecureLogger(key=key, log_path=log_path)
    return _default
