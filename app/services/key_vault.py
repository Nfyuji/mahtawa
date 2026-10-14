from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken


PREFIX = "enc:v1:"


def encrypt_api_key(api_key: str, secret_key: str) -> str:
    clean = api_key.strip()
    if not clean:
        return ""
    token = _fernet(secret_key).encrypt(clean.encode("utf-8")).decode("ascii")
    return PREFIX + token


def decrypt_api_key(stored_value: str | None, secret_key: str) -> str:
    value = (stored_value or "").strip()
    if not value:
        return ""
    # Support keys saved by the older release, then encrypt them on next save.
    if not value.startswith(PREFIX):
        return value
    try:
        return (
            _fernet(secret_key)
            .decrypt(value[len(PREFIX) :].encode("ascii"))
            .decode("utf-8")
        )
    except (InvalidToken, ValueError, UnicodeError):
        return ""


def _fernet(secret_key: str) -> Fernet:
    digest = hashlib.sha256(secret_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))
