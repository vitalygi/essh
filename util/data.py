import base64
import os
import json
import traceback
from contextlib import suppress
from ipaddress import ip_address
from typing import List, Union
import secrets
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import dotenv
dotenv.load_dotenv()

try:
    DIR_PATH = f'{os.path.expanduser(os.getenv("DATA_DIR_PATH"))}'
    if DIR_PATH is None:
        raise TypeError
except TypeError:
    raise Exception('DATA_DIR_PATH not found in .env')

SALT_PATH = f'{DIR_PATH}/.salt'
DATA_PATH = f'{DIR_PATH}/.essh'
TERM_SESSION = f'{DIR_PATH}/.esession'

try:
    os.makedirs(DIR_PATH, exist_ok=True)
except NotADirectoryError:
    raise Exception('.essh is not a directory, but exists, delete this file yourself, please')

class PasswordEntity(dict):
    """A dictionary-based class to store password-related information."""
    def __init__(self, **kwargs):
        self.ip_address = kwargs.get('ip_address')
        self.name = kwargs.get('name', None)
        self.user = kwargs.get('user') or 'root'
        self.password = kwargs.get('password')
        super().__init__({
            'ip_address': self.ip_address,
            'name': self.name,
            'user': self.user,
            'password': self.password
        })

def get_engine(password: str, salt: str) -> Fernet:
    """Create a Fernet encryption engine using a password and salt.

    Args:
        password (str): The password used to derive the key.
        salt (str): The salt used in the key derivation function.

    Returns:
        Fernet: A Fernet encryption object configured with the derived key.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
    return Fernet(key)

def encrypt_string(password: str, data: str, salt, file_path: str = DATA_PATH) -> bytes:
    """Encrypt a string and write the encrypted bytes to a file.

    Args:
        password (str): Password used for encryption.
        data (str): The data to encrypt.
        salt: Salt for encryption.
        file_path (str): Path to the file where encrypted data is stored.

    Returns:
        bytes: Encrypted data.
    """
    encrypted_data = get_engine(password, salt).encrypt(data.encode('utf-8'))
    write_file(file_path, encrypted_data)
    return encrypted_data

def encrypt_json(password: str, data, salt, file_path: str = DATA_PATH) -> bytes:
    """Encrypt JSON data and store it in a file.

    Args:
        password (str): Password for encryption.
        data: Data to be JSON-serialized and encrypted.
        salt: Salt for encryption.
        file_path (str): File path to save the encrypted data.

    Returns:
        bytes: Encrypted JSON data.
    """
    return encrypt_string(password, json.dumps(data), salt, file_path)

def decrypt(password: str, salt, data: bytes = None, file_path: str = DATA_PATH):
    """Decrypt data from a file or from provided bytes.

    Args:
        password (str): The password used for decryption.
        salt: Salt for decryption.
        data (bytes, optional): Encrypted data to decrypt. Defaults to None.
        file_path (str): Path to file with the encrypted data.

    Returns:
        Object: Decrypted JSON data, parsed from the original JSON.
    """
    try:
        if data is None:
            data = read_file(file_path)
        decrypted_data = get_engine(password, salt).decrypt(data)
        return json.loads(decrypted_data.decode("utf-8"))
    except InvalidToken:
        return None
    except FileNotFoundError:
        return []

def decrypt_passwords(password: str, encrypted_data: bytes = None, file_path: str = DATA_PATH) -> Union[List[PasswordEntity], None]:
    """Decrypt a list of PasswordEntity objects.

    Args:
        password (str): Password for decryption.
        encrypted_data (bytes, optional): Encrypted data to decrypt. Defaults to None.
        file_path (str): Path to file with encrypted data.

    Returns:
        Union[List[PasswordEntity], None]: The decrypted PasswordEntity objects or None on failure.
    """
    decrypted_data = decrypt(password, get_salt(), encrypted_data, file_path)
    if decrypted_data is None:
        return None
    else:
        return [PasswordEntity(**obj) for obj in decrypted_data]

def find_server(entities: List[PasswordEntity], data: str):
    """Find a server entity by IP or name.

    Args:
        entities (List[PasswordEntity]): List of server entities to search.
        data (str): Search key, either an IP or a server name.

    Returns:
        PasswordEntity or None: The matching server entity, if found.
    """
    if is_ip_valid(data):
        arr = [obj for obj in entities if obj.ip_address == data]
    else:
        arr = [obj for obj in entities if obj.name == data]
    return arr[0] if len(arr) == 1 else None

def read_file(file_path) -> bytes:
    """Read bytes from a file.

    Args:
        file_path (str): Path to the file to read.

    Returns:
        bytes: Content of the file.
    """
    with open(file_path, 'rb') as f:
        return f.read(-1)

def write_file(file_path, data: bytes) -> int:
    """Write bytes to a file.

    Args:
        file_path (str): Path to the file to write to.
        data (bytes): Data to write.

    Returns:
        int: Number of bytes written.
    """
    with open(file_path, 'wb') as f:
        return f.write(data)

def write_term_session(term_session_id, master_pass, file_path=TERM_SESSION):
    """Encrypt and store the master password for the terminal session.

    Args:
        term_session_id (str): Terminal session identifier.
        master_pass (str): Master password to encrypt and store.
        file_path (str, optional): File path to save the session data. Defaults to TERM_SESSION.
    """
    encrypt_string(term_session_id, master_pass, get_salt(), file_path)

def read_previous_term_session(term_session_id: str, file_path=TERM_SESSION) -> Union[str, None]:
    """Read the stored master password for the terminal session.

    Args:
        term_session_id (str): Terminal session identifier.
        file_path (str, optional): Path to the session file. Defaults to TERM_SESSION.

    Returns:
        Union[str, None]: Decrypted master password or None if not found.
    """
    try:
        previous_session = read_file(file_path)
    except FileNotFoundError:
        previous_session = None
    if previous_session is not None:
        try:
            decrypted_data = get_engine(term_session_id, get_salt()).decrypt(previous_session)
            return decrypted_data.decode("utf-8")
        except Exception:
            return None

def get_salt():
    """Retrieve or generate a salt for encryption.

    Returns:
        str: The salt used for cryptographic operations.
    """
    try:
        s = read_file(SALT_PATH)
        s = s.decode()
    except FileNotFoundError:
        s = secrets.token_urlsafe(64)
        write_file(SALT_PATH, s.encode())
    return s

def is_ip_valid(ip):
    """Check if a given string is a valid IP address.

    Args:
        ip (str): The string to check.

    Returns:
        bool: True if valid, False otherwise.
    """
    with suppress(ValueError):
        return ip_address(ip)
    return None