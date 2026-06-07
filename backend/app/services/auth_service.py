import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.schemas.auth import UserCreate


class AuthService:
    def get_by_email(self, db: Session, email: str):
        return db.query(User).filter(User.email == email.lower()).first()

    def get(self, db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    def create_user(self, db: Session, user_in: UserCreate):
        user = User(
            email=user_in.email.lower(),
            full_name=user_in.full_name,
            hashed_password=self.hash_password(user_in.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate(self, db: Session, email: str, password: str):
        user = self.get_by_email(db, email)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    def hash_password(self, password: str) -> str:
        salt = os.urandom(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
        return f"pbkdf2_sha256${self._b64(salt)}${self._b64(digest)}"

    def verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            algorithm, salt_b64, digest_b64 = stored_hash.split("$", 2)
            if algorithm != "pbkdf2_sha256":
                return False
            salt = self._unb64(salt_b64)
            expected = self._unb64(digest_b64)
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
            return hmac.compare_digest(actual, expected)
        except ValueError:
            return False

    def create_access_token(self, user: User) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=settings.auth_token_expire_minutes)).timestamp()),
        }
        header = {"alg": "HS256", "typ": "JWT"}
        signing_input = f"{self._json_b64(header)}.{self._json_b64(payload)}"
        signature = self._sign(signing_input)
        return f"{signing_input}.{signature}"

    def verify_access_token(self, token: str) -> dict | None:
        try:
            header_b64, payload_b64, signature = token.split(".")
            signing_input = f"{header_b64}.{payload_b64}"
            if not hmac.compare_digest(self._sign(signing_input), signature):
                return None
            payload = json.loads(self._unb64(payload_b64).decode("utf-8"))
            if int(payload.get("exp", 0)) < int(datetime.now(timezone.utc).timestamp()):
                return None
            return payload
        except Exception:
            return None

    def _sign(self, value: str) -> str:
        digest = hmac.new(settings.auth_secret_key.encode("utf-8"), value.encode("utf-8"), hashlib.sha256).digest()
        return self._b64(digest)

    def _json_b64(self, value: dict) -> str:
        return self._b64(json.dumps(value, separators=(",", ":")).encode("utf-8"))

    def _b64(self, value: bytes) -> str:
        return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")

    def _unb64(self, value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding)
