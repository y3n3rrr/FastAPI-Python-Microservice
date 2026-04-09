import base64
import hashlib
import hmac
import json
import secrets
from datetime import UTC, datetime, timedelta

from app.core.config import get_settings


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}")


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return f"{salt}${password_hash}"


def verify_password(password: str, stored_password_hash: str) -> bool:
    try:
        salt, expected_hash = stored_password_hash.split("$", 1)
    except ValueError:
        return False

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()
    return hmac.compare_digest(password_hash, expected_hash)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_access_token_expire_minutes)).timestamp()),
    }
    header = {"alg": "HS256", "typ": "JWT"}

    encoded_header = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}"
    signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    encoded_signature = _b64url_encode(signature)
    return f"{signing_input}.{encoded_signature}"


def decode_access_token(token: str) -> dict[str, object] | None:
    settings = get_settings()

    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".")
    except ValueError:
        return None

    signing_input = f"{encoded_header}.{encoded_payload}"
    expected_signature = hmac.new(
        settings.jwt_secret_key.encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    try:
        actual_signature = _b64url_decode(encoded_signature)
    except Exception:
        return None

    if not hmac.compare_digest(actual_signature, expected_signature):
        return None

    try:
        payload = json.loads(_b64url_decode(encoded_payload))
    except Exception:
        return None

    expires_at = payload.get("exp")
    if not isinstance(expires_at, int):
        return None

    if expires_at < int(datetime.now(UTC).timestamp()):
        return None

    return payload
