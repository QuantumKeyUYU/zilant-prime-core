# mypy: ignore-errors
"""
Минимальный shim, достаточный для теста s3_backend.
"""

from botocore.session import get_session


def client(service_name: str, *args, **kwargs):
    """Вернёт «клиент», который потом оборачивается Stubber-ом."""
    return get_session().create_client(service_name, *args, **kwargs)
