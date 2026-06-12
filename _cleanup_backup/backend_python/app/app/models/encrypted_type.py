from __future__ import annotations

from sqlalchemy.types import TypeDecorator, VARCHAR

from app.core.encryption import decrypt_value, encrypt_value


class EncryptedString(TypeDecorator):
    impl = VARCHAR
    cache_ok = True

    def process_bind_param(self, value, dialect):  # noqa: ANN001
        if value is None:
            return None
        return encrypt_value(value)

    def process_result_value(self, value, dialect):  # noqa: ANN001
        if value is None:
            return None
        return decrypt_value(value)
