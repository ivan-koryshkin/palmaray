import base64
import hashlib

from cryptography.fernet import Fernet
from sqlalchemy.types import TypeDecorator, String
from sqlalchemy.engine import Dialect

from settings import settings


_FERNET_KEY = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode()).digest())
_FERNET = Fernet(_FERNET_KEY)


class EncryptedType(TypeDecorator):
    impl = String

    cache_ok = True

    def process_bind_param(self, value: str | bytes | None, dialect: Dialect) -> str | None:
        if value is None:
            return None
        if not isinstance(value, (str, bytes)):
            value = str(value)
        if isinstance(value, str):
            token = _FERNET.encrypt(value.encode())
        else:
            token = _FERNET.encrypt(value)
        return token.decode()

    def process_result_value(self, value: str | None, dialect: Dialect) -> str | None:
        if value is None:
            return None
        plain = _FERNET.decrypt(value.encode())
        return plain.decode()
