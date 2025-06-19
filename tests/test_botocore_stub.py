# tests/test_botocore_stub.py
import boto3
import botocore
from botocore import stub


def test_get_session_and_client():
    sess = botocore.get_session()
    assert hasattr(sess, "create_client")

    client = sess.create_client("s3")
    resp_put = client.put_object(Bucket="x", Key="y", Body=b"data")
    assert resp_put == {"ETag": "deadbeef"}

    resp_get = client.get_object(Bucket="x", Key="y")
    assert "Body" in resp_get
    # Body.read() для пустого буфера
    assert resp_get["Body"].read() == b""


def test_boto3_client_alias():
    client = boto3.client("s3")
    result = client.get_object(Key="k")
    assert "Body" in result
    assert hasattr(result["Body"], "read")


def test_ANY_and_Stubber_behavior():
    a = stub.ANY()
    # __eq__ всегда возвращает True
    assert a == "любой"
    assert a == 123

    class Dummy:
        def foo(self, **kw):
            return None

    client = Dummy()
    st = stub.Stubber(client)
    st.add_response("foo", {"ok": True}, {"x": 1})
    st.activate()
    assert client.foo(x=1) == {"ok": True}
    st.deactivate()
