from getpass import getpass
from util.data import get_salt
from util.data import (encrypt_json,
                       PasswordEntity, find_server)
from util.router import Router
from util.service import connect_via_ssh_with_password

router = Router()


@router.handle_arg(require_password=False)
def drop():
    new_master_pass = getpass('Enter new master password(all your data will be wiped): ')
    while len(new_master_pass) <= 0:
        new_master_pass = getpass('Master password cannot be 0 length, try again: ')
    encrypt_json(new_master_pass, [], get_salt())
    return print('Database successfully dropped. New password set.')


@router.handle_arg()
def data(data, passwords):
    server = find_server(passwords, data)
    if server is not None:
        connect_via_ssh_with_password(server.ip_address, server.password, server.user)
    else:
        print('Server was not found')


@router.handle_arg()
def change(passwords):
    new_master_pass = getpass('Enter new master password: ')
    while len(new_master_pass) <= 0:
        new_master_pass = getpass('Master password cannot be 0 length, try again: ')
    encrypt_json(new_master_pass, passwords, get_salt())
    print('Master password successfully changed')


@router.handle_arg()
def add(ip_address, password, name, user, passwords, master_pass):
    if not all([ip_address, password]):
        return print('To add a server, provide IP(4/6) and password')
    passwords.append(PasswordEntity(ip_address=ip_address,
                                    password=password,
                                    user=user,
                                    name=name))
    encrypt_json(master_pass, passwords, get_salt())
    print('Server successfully set:', f"IP:{ip_address}")
