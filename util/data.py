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

DIR_PATH = f'{os.path.expanduser("~")}/.essh'

SALT_PATH = f'{DIR_PATH}/.salt'
DATA_PATH = f'{DIR_PATH}/.essh'
TERM_SESSION = f'{DIR_PATH}/.esession'
try:
    os.makedirs(DIR_PATH, exist_ok=True)
except NotADirectoryError:
    raise Exception('.essh is not directory, but exists, delete this file yourself, please')


class PasswordEntity(dict):

    def __init__(self, **kwargs):
        self.ip_address = kwargs.get('ip_address')
        self.name = kwargs.get('name', None)
        self.user = kwargs.get('user') or 'root'
        self.password = kwargs.get('password')
        super().__init__(
            {'ip_address': self.ip_address, 'name': self.name, 'user': self.user, 'password': self.password})


def get_engine(password: str, salt: str) -> Fernet:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
    return Fernet(key)

def encrypt_string(password: str, data: str, salt, file_path: str = DATA_PATH) -> bytes:
    encrypted_data = get_engine(password, salt).encrypt(data.encode('utf-8'))
    write_file(file_path, encrypted_data)
    return encrypted_data


def encrypt_json(password: str, data, salt, file_path: str = DATA_PATH) -> bytes:
    return encrypt_string(password,json.dumps(data),salt,file_path)


def decrypt(password: str, salt, data: bytes = None, file_path: str = DATA_PATH):
    try:
        if data is None:
            data = read_file(file_path)
        decrypted_data = get_engine(password, salt).decrypt(data)
        return json.loads(decrypted_data.decode("utf-8"))
    except InvalidToken:
        return None
    except FileNotFoundError:
        return []


def decrypt_passwords(password: str, encrypted_data: bytes = None, file_path: str = DATA_PATH) \
        -> Union[List[PasswordEntity], None]:
    decrypted_data = decrypt(password, get_salt(), encrypted_data, file_path)
    if decrypted_data is None:
        return None
    else:
        return [PasswordEntity(**obj) for obj in decrypted_data]


def find_server(entities: List[PasswordEntity], data: str):
    if is_ip_valid(data):
        arr = [obj for obj in entities if obj.ip_address == data]
    else:
        arr = [obj for obj in entities if obj.name == data]
    return arr[0] if len(arr) == 1 else None


def read_file(file_path) -> bytes:
    with open(file_path, 'rb') as f:
        return f.read(-1)


def write_file(file_path, data: bytes) -> int:
    with open(file_path, 'wb') as f:
        return f.write(data)

def write_term_session(term_session_id,master_pass,file_path=TERM_SESSION):
    encrypt_string(term_session_id, master_pass, get_salt(), file_path)

def read_previous_term_session(term_session_id: str,file_path=TERM_SESSION) -> Union[str,None]:
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
    try:
        s = read_file(SALT_PATH)
        s = s.decode()
    except FileNotFoundError:
        s = secrets.token_urlsafe(64)
        write_file(SALT_PATH, s.encode())
    return s


def is_ip_valid(ip):
    with suppress(ValueError):
        return ip_address(ip)
    return None
