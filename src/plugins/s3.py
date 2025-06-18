"""Example plugin for S3 backend."""

from . import __name__  # noqa: F401  # make namespace package


def name() -> str:
    return "s3"
