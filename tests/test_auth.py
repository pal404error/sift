from __future__ import annotations

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from llm_search.auth import (
    ApiKeyVerifier,
    OidcVerifier,
    audit,
    parse_api_keys,
    require_role,
)
from llm_search.config import Settings


def test_parse_api_keys():
    keys = parse_api_keys("admin:KEY1,user:KEY2")
    assert keys == {"KEY1": "admin", "KEY2": "user"}


def test_parse_api_keys_ignores_empty():
    assert parse_api_keys("") == {}
    assert parse_api_keys("badformat") == {}


def test_apikey_verifier_maps_role_and_subject():
    v = ApiKeyVerifier(parse_api_keys("admin:AAA,user:BBB"))
    assert v.verify("AAA") == ("admin", "apikey:admin")
    assert v.verify("BBB") == ("user", "apikey:user")
    assert v.verify("ZZZ") is None


def _make_oidc(issuer="https://idp", audience="llm", roles=("admin",)):
    from cryptography.hazmat.primitives.asymmetric import rsa
    from jwt.algorithms import RSAAlgorithm

    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pub = priv.public_key()
    jwk = __import__("json").loads(RSAAlgorithm.to_jwk(pub))
    jwk["kid"] = "k1"
    jwks = {"keys": [jwk]}

    import jwt

    token = jwt.encode(
        {"iss": issuer, "aud": audience, "sub": "u1", "roles": list(roles)},
        priv,
        algorithm="RS256",
        headers={"kid": "k1"},
    )
    v = OidcVerifier(issuer=issuer, audience=audience, get_jwks=lambda: jwks)
    return v, token


def test_oidc_verifier_verifies_signature_and_extracts_role():
    v, token = _make_oidc(roles=("admin",))
    assert v.verify(token) == ("admin", "oidc:u1")


def test_oidc_verifier_rejects_wrong_issuer():
    v, token = _make_oidc(issuer="https://idp")
    # re-sign with a different issuer but reuse verifier expecting https://idp
    from cryptography.hazmat.primitives.asymmetric import rsa
    from jwt.algorithms import RSAAlgorithm

    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = __import__("json").loads(RSAAlgorithm.to_jwk(priv.public_key()))
    jwk["kid"] = "k1"
    import jwt

    bad = jwt.encode(
        {"iss": "https://evil", "aud": "llm", "sub": "u1", "roles": ["admin"]},
        priv,
        algorithm="RS256",
        headers={"kid": "k1"},
    )
    assert v.verify(bad) is None


def test_oidc_verifier_rejects_no_role():
    v, token = _make_oidc(roles=())
    assert v.verify(token) is None


def test_oidc_verifier_rejects_tampered_signature():
    v, token = _make_oidc(roles=("admin",))
    # corrupt a mid-signature char (last char is padding/noise; skip it)
    parts = token.split(".")
    c = parts[2][8]
    alt = "A" if c != "A" else "B"
    parts[2] = parts[2][:8] + alt + parts[2][9:]
    assert v.verify(".".join(parts)) is None


def test_require_role_open_when_auth_disabled():
    dep = require_role("user")

    class Req:
        client = None

    s = Settings(require_auth=False)
    assert dep(request=Req(), creds=None, settings=s) == "anonymous"


def test_require_role_rejects_missing_token():
    dep = require_role("user")

    class Req:
        client = None

    s = Settings(require_auth=True, api_keys="user:KEY")
    with pytest.raises(HTTPException) as e:
        dep(request=Req(), creds=None, settings=s)
    assert e.value.status_code == 401


def test_require_role_rejects_insufficient_role():
    dep = require_role("admin")

    class Req:
        client = None

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="USERKEY")
    s = Settings(require_auth=True, api_keys="user:USERKEY")
    with pytest.raises(HTTPException) as e:
        dep(request=Req(), creds=creds, settings=s)
    assert e.value.status_code == 403


def test_require_role_allows_with_role():
    dep = require_role("admin")

    class Req:
        client = None

    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="ADMKEY")
    s = Settings(require_auth=True, api_keys="admin:ADMKEY")
    assert dep(request=Req(), creds=creds, settings=s) == "admin"


def test_audit_writes_log(tmp_path):
    log = tmp_path / "audit.log"
    audit("test", "alice", None, ok=True, settings=Settings(audit_log=str(log)))
    assert log.exists()
    assert "alice" in log.read_text()
