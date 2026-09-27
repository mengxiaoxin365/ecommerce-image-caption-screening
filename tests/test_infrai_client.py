import io
import json
import urllib.error

from infrai_client import InfraiClient


class Response:
    status = 200
    headers = {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read(self):
        return b'{"ok": true, "data": {"flagged": false}}'


def test_moderation_request_uses_contract_fields(monkeypatch):
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    requests = []

    def urlopen(request, timeout):
        requests.append(json.loads(request.data))
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    assert InfraiClient().moderate_image("image-id") == {"flagged": False}
    assert requests == [{"image": "image-id", "ops": ["moderate"]}]


def test_rate_limit_retries_before_raising_envelope(monkeypatch):
    monkeypatch.setenv("INFRAI_API_KEY", "test-key")
    calls = []
    monkeypatch.setattr("time.sleep", lambda seconds: None)

    def urlopen(request, timeout):
        calls.append(request)
        if len(calls) == 1:
            raise urllib.error.HTTPError(
                request.full_url, 429, "rate limited", {"Retry-After": "1"},
                io.BytesIO(b'{"ok": false, "error": {"code": "RATE_LIMITED"}}'),
            )
        return Response()

    monkeypatch.setattr("urllib.request.urlopen", urlopen)
    assert InfraiClient().moderate_image("image-id") == {"flagged": False}
    assert len(calls) == 2
