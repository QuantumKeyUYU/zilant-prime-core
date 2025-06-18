"""AWS S3 storage backend."""

from __future__ import annotations

import uuid

import boto3

BUCKET = "zilant-bucket"


def store(container: bytes) -> str:
    client = boto3.client("s3")
    key = f"{uuid.uuid4().hex}.zil"
    client.put_object(Bucket=BUCKET, Key=key, Body=container)
    return f"s3://{BUCKET}/{key}"


def retrieve(uri: str) -> bytes:
    prefix = f"s3://{BUCKET}/"
    if not uri.startswith(prefix):
        raise ValueError("Invalid URI")
    key = uri[len(prefix) :]
    client = boto3.client("s3")
    obj = client.get_object(Bucket=BUCKET, Key=key)
    return obj["Body"].read()
