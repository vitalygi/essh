import argparse
import base64
import os
import json
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from ipaddress import ip_address
from contextlib import suppress
from getpass import getpass
import subprocess

import pexpect

DATA_PATH = f'{os.getenv("HOME")}/.essh'
SALT = b'URmMAfHhZJcvmNZ_hirZ_1rwPCX-ibTDX33a'
ITERATIONS = 480000
DEFAULT_PASS = 'VmfriGduvpA434-bbb9fdfs-ndgreozcu5cv4'
def ip_address_validator(ip):
    with suppress(ValueError):
        return ip_address(ip)
    return None

def connect_via_ssh(ip, server_pass,user, port=22,clear=False):
    try:
        ssh_command = f"ssh {user}@{ip} -p {port}"
        child = pexpect.spawn(ssh_command)
        child.expect("password:")
        child.sendline(server_pass)
        if clear: os.system('cls' if os.name == 'nt' else 'clear')
        child.interact()
    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"SSH connection failed: {e}")
        
def get_engine(password: str) -> Fernet:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=ITERATIONS,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
    return Fernet(key)

def encrypt_data(password: str, data: dict) -> bytes:
    encrypted_data = get_engine(password).encrypt(json.dumps(data).encode('utf-8'))
    with open(DATA_PATH, 'wb') as f:
        f.write(encrypted_data)
    return encrypted_data

def decrypt_data(password: str):
    try:
        with open(DATA_PATH, 'rb') as f:
            data = f.read()
            if not data:
                raise ValueError("Empty data file")
            decrypted_data = get_engine(password).decrypt(data)
            return json.loads(decrypted_data.decode("utf-8"))
    except (InvalidToken, ValueError):
        return None
    except FileNotFoundError:
        return {}

def main():
    parser = argparse.ArgumentParser(prog='SSH_Manager', description='Manage SSH server configurations securely.')
    parser.add_argument('-a', '--add', help='Add a new server flag', action='store_true')
    parser.add_argument('-ip', '--ip_address', help='IP(4/6) address of the server')
    parser.add_argument('-p', '--password', help='Password for the server')
    parser.add_argument('-n', '--name', help='Name of the server')
    parser.add_argument('-u','--user',help='User for server')
    parser.add_argument('-c', '--change', action='store_true',help='Change master password flag')
    parser.add_argument('data', help='Enter IP or name to fetch details', nargs='?', default=None)
    args = parser.parse_args()

    while True:
        master_pass = getpass('Enter master password: ')
        if len(master_pass)==0:
            master_pass = DEFAULT_PASS 
            data = decrypt_data(master_pass)
            data = {} if data is None else data
        else:
            data = decrypt_data(master_pass)
        if data is not None:
            break

    if args.data is not None:
        if ip_address_validator(args.data):
            server = data.get(args.data, None)
            if server is not None:
                connect_via_ssh(args.data,server['p'],server['u'])
        else:
            ip = data.get(args.data)
            if ip:
                connect_via_ssh(ip,data.get(ip)['p'],data.get(ip)['u'])
            else:
                print('Server with this name not found')
    if args.change:
        master_pass = master_pass = getpass('Enter master password: ')
        encrypt_data(args.change,data)
        print('Master password successfully changed')
    if args.add:
        if not all([args.ip_address, args.password]):
            print('To add a server, provide IP(4/6) and password')
            return
        data[args.ip_address] = {'p':args.password,'u':args.user 
                                 if args.user is not None else 'root'}
        if args.name is not None:
            data[args.name] = args.ip_address
        encrypt_data(master_pass, data)
        print('Server successfully set:', args.ip_address, args.password)

if __name__ == '__main__':
    main()
