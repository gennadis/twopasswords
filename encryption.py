import os
import dotenv
from typing import Union
from cryptography.fernet import Fernet

dotenv.load_dotenv()
key_path = os.environ.get("SECRET_KEY")


class EncryptionEngine:
    """
    This class is responsible for all the Encryption / Decryption
    operations needed in the code such as:
    - key file generation
    - key file loading
    - encryption str object to bytes
    - decryption bytes type to string
    """

    def __init__(self):
        self.key_file = key_path
        self._generate_key()
        self.fernet_obj = self._load_key()

    def _generate_key(self) -> None:
        key = Fernet.generate_key()
        with open(self.key_file, "wb") as keyfile:
            keyfile.write(key)

    def _load_key(self) -> Fernet:
        key = open(self.key_file, "rb").read()
        return Fernet(key)

    def encrypt(self, raw_password: str) -> bytes:
        bytes_pass = raw_password.encode()
        return self.fernet_obj.encrypt(bytes_pass)

    def decrypt(self, encrypted_password: bytes) -> str:
        decrypted_data = self.fernet_obj.decrypt(encrypted_password)
        return decrypted_data.decode()


if __name__ == "__main__":
    encryption_engine = EncryptionEngine()
    password = "P@sSw0rD"
    print(f"Should encrypt this password: {password}")
    print("*" * 30)

    encrypted_passw = encryption_engine.encrypt(password)
    print(f"Encrypted password in bytes string: {encrypted_passw}")
    print("*" * 30)

    dectypted_passw = encryption_engine.decrypt(encrypted_passw)
    print(f"Password that was decrypted: {dectypted_passw}")
