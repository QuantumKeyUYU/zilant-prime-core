import io
from unittest import mock

from backends import s3_backend


class DummyClient:
    def __init__(self):
        self.blob = None

    def put_object(self, Bucket, Key, Body):
        self.blob = Body
        self.key = Key

    def get_object(self, Bucket, Key):
        assert Key == self.key
        return {"Body": io.BytesIO(self.blob)}


def test_s3_store_retrieve(monkeypatch):
    client = DummyClient()
    monkeypatch.setattr(s3_backend, "boto3", mock.Mock(client=lambda name: client))
    uri = s3_backend.store(b"data")
    assert uri.startswith("s3://")
    out = s3_backend.retrieve(uri)
    assert out == b"data"
