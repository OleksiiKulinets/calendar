from cryptography.fernet import Fernet
import os


class CryptoService:

    _fernet = Fernet(
        os.getenv("ENCRYPTION_KEY").encode()
    )

    @classmethod
    def encrypt(
        cls,
        value: str,
    ) -> str:

        return cls._fernet.encrypt(
            value.encode()
        ).decode()

    @classmethod
    def decrypt(
        cls,
        value: str,
    ) -> str:

        return cls._fernet.decrypt(
            value.encode()
        ).decode()