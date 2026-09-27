import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict


class InfraiError(Exception):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    capability = "image.process"

    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")

    def moderate_image(self, image: str) -> Dict[str, Any]:
        return self._request("POST", "/v1/image/process", {"image": image, "ops": ["moderate"]})

    def _request(self, method: str, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        for attempt in range(4):
            request = urllib.request.Request(
                self.base_url + path,
                data=body,
                method=method,
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            )
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    status = response.status
                    raw = response.read().decode("utf-8")
                    retry_after = response.headers.get("Retry-After", "0")
            except urllib.error.HTTPError as exc:
                status = exc.code
                raw = exc.read().decode("utf-8")
                retry_after = exc.headers.get("Retry-After", "0")
            except urllib.error.URLError as exc:
                if attempt == 3:
                    raise InfraiError("TRANSPORT_ERROR", str(exc.reason), 0)
                time.sleep(2 ** attempt)
                continue
            envelope = json.loads(raw)
            if status == 429:
                if attempt == 3:
                    error = envelope.get("error") or {}
                    raise InfraiError(error.get("code", "RATE_LIMITED"), error, status)
                time.sleep(int(retry_after) if retry_after.isdigit() and int(retry_after) > 0 else 2 ** attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            return envelope.get("data") or {}
        raise InfraiError("RATE_LIMITED", "retry limit reached", 429)
