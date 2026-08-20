from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Protocol, cast

try:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
except ImportError:  # pragma: no cover
    RSAPublicKey = object  # type: ignore[assignment, misc]

from fastapi import Depends, HTTPException, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from llm_search.config import Settings, get_settings

ROLE_RANK = {"user": 1, "admin": 2}

_bearer = HTTPBearer(auto_error=False)
_audit_buffer: list[str] = []


def parse_api_keys(raw: str) -> dict[str, str]:
    """Parse 'role:key,role:key' into {key: role}."""
    keys: dict[str, str] = {}
    for part in raw.split(","):
        part = part.strip()
        if not part or ":" not in part:
            continue
        role, key = part.split(":", 1)
        keys[key.strip()] = role.strip().lower()
    return keys


class TokenVerifier(Protocol):
    def verify(self, token: str) -> tuple[str, str] | None:
        """Return (role, subject) or None if invalid."""


class ApiKeyVerifier:
    def __init__(self, keys: dict[str, str]) -> None:
        self.keys = keys

    def verify(self, token: str) -> tuple[str, str] | None:
        role = self.keys.get(token)
        if role is None:
            return None
        return role, f"apikey:{role}"


class OidcVerifier:
    """Verify OIDC JWT bearer tokens by JWKS signature check (SSO-ready).

    For tests/air-gapped use, inject `get_jwks` (returns a JWKS dict) to bypass the
    network discovery of `{issuer}/.well-known/...`.
    """

    def __init__(
        self,
        issuer: str,
        audience: str,
        role_claim: str = "roles",
        get_jwks: Callable[[], dict] | None = None,
    ) -> None:
        self.issuer = issuer
        self.audience = audience
        self.role_claim = role_claim
        self._get_jwks = get_jwks

    def _fetch_jwks(self) -> dict:
        if self._get_jwks:
            return self._get_jwks()
        try:
            import httpx
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("httpx required for OIDC discovery") from e
        cfg = httpx.get(f"{self.issuer}/.well-known/openid-configuration", timeout=10).json()
        return httpx.get(cfg["jwks_uri"], timeout=10).json()

    def verify(self, token: str) -> tuple[str, str] | None:
        try:
            import jwt
            from jwt.algorithms import RSAAlgorithm
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("PyJWT required for OIDC: pip install pyjwt") from e
        try:
            jwks = self._fetch_jwks()
            header = jwt.get_unverified_header(token)
            key = next((k for k in jwks.get("keys", []) if k.get("kid") == header.get("kid")), None)
            if key is None:
                return None
            public_key = cast(
                "RSAPublicKey",
                RSAAlgorithm.from_jwk(__import__("json").dumps(key)),
            )
            claims = jwt.decode(
                token,
                key=public_key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
            )
        except Exception:
            return None
        roles = claims.get(self.role_claim, [])
        roles = [roles] if isinstance(roles, str) else roles
        if "admin" in roles:
            role = "admin"
        elif "user" in roles:
            role = "user"
        else:
            return None
        return role, f"oidc:{claims.get('sub', 'unknown')}"


def build_verifier(settings: Settings | None = None) -> TokenVerifier:
    s = settings or get_settings()
    if s.auth_method == "oidc":
        return OidcVerifier(
            issuer=s.oidc_issuer, audience=s.oidc_audience, role_claim=s.oidc_role_claim
        )
    return ApiKeyVerifier(parse_api_keys(s.api_keys))


def audit(
    action: str,
    principal: str | None,
    request: Request | None,
    ok: bool,
    settings: Settings | None = None,
) -> None:
    s = settings or get_settings()
    if not s.audit_log:
        return
    entry = {
        "ts": time.time(),
        "action": action,
        "principal": principal,
        "ok": ok,
        "ip": request.client.host if request and request.client else None,
    }
    line = json.dumps(entry)
    try:
        with open(s.audit_log, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        _audit_buffer.append(line)


def require_role(required: str = "user"):
    def dependency(
        request: Request,
        creds: HTTPAuthorizationCredentials | None = Security(_bearer),  # noqa: B008
        settings: Settings = Depends(get_settings),  # noqa: B008
    ) -> str:
        if not settings.require_auth:
            return "anonymous"
        if creds is None or not creds.credentials:
            audit("auth", "missing", request, ok=False, settings=settings)
            raise HTTPException(status_code=401, detail="Missing bearer token")
        role, subject = build_verifier(settings).verify(creds.credentials) or (None, None)
        if role is None:
            audit("auth", "unknown", request, ok=False, settings=settings)
            raise HTTPException(status_code=401, detail="Invalid token")
        if ROLE_RANK.get(role, 0) < ROLE_RANK.get(required, 0):
            audit(f"role:{required}", subject, request, ok=False, settings=settings)
            raise HTTPException(status_code=403, detail="Insufficient role")
        audit(f"role:{required}", subject, request, ok=True, settings=settings)
        return role

    return dependency
