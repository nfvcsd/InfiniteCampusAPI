import threading
import time

import requests

from ..exceptions import AuthenticationError, ResponseDecodeError, TransportError


class Auth:
    url: str
    key: str
    secret: str
    base_url: str

    def __init__(
        self,
        token_url,
        key,
        secret,
        base_url,
        session=None,
        timeout=30,
        refresh_margin=60,
    ):
        self.token_url = token_url
        self.key = key
        self.secret = secret
        self.base_url = base_url
        self.session = session if session is not None else requests.Session()
        self.timeout = timeout
        self.refresh_margin = refresh_margin
        self._access_token: str | None = None
        self._expires_at = 0.0
        self._effective_refresh_margin = 0.0
        self._token_lock = threading.Lock()
        self.refresh(force=True)

    @property
    def access_token(self) -> str:
        """Return a usable token, refreshing it before it expires."""
        if self.is_expired:
            return self.refresh()
        return self._access_token

    @property
    def is_expired(self) -> bool:
        return time.monotonic() >= (self._expires_at - self._effective_refresh_margin)

    def refresh(self, *, force=False) -> str:
        """Refresh the token when needed, or unconditionally when forced."""
        with self._token_lock:
            if not force and self._access_token is not None and not self.is_expired:
                return self._access_token

            payload = self._request_token()
            try:
                access_token = payload["access_token"]
            except (KeyError, TypeError) as exc:
                raise AuthenticationError(
                    "Authentication response did not include an access token",
                    status_code=200,
                    endpoint=self.token_url,
                ) from exc

            try:
                expires_in = max(0.0, float(payload.get("expires_in", 300)))
            except (TypeError, ValueError) as exc:
                raise AuthenticationError(
                    "Authentication response included an invalid expires_in value",
                    status_code=200,
                    endpoint=self.token_url,
                ) from exc

            self._access_token = access_token
            self._expires_at = time.monotonic() + expires_in
            self._effective_refresh_margin = min(
                float(self.refresh_margin), expires_in * 0.1
            )
            return access_token

    def _request_token(self) -> dict:
        url = self.token_url
        data = {
            "grant_type": "client_credentials",
            "client_id": self.key,
            "client_secret": self.secret,
        }

        try:
            response = self.session.post(url, data=data, timeout=self.timeout)
        except requests.RequestException as exc:
            raise TransportError("Unable to reach the authentication endpoint") from exc

        if not 200 <= response.status_code < 300:
            raise AuthenticationError(
                f"Authentication failed with status code {response.status_code}",
                status_code=response.status_code,
                endpoint=url,
            )

        try:
            payload = response.json()
        except (requests.exceptions.JSONDecodeError, ValueError) as exc:
            raise ResponseDecodeError(
                "The authentication endpoint returned invalid JSON"
            ) from exc

        if not isinstance(payload, dict):
            raise AuthenticationError(
                "Authentication response must be a JSON object",
                status_code=response.status_code,
                endpoint=url,
            )
        return payload
