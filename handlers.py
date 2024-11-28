from getpass import getpass
from util.data import get_salt
from util.data import encrypt_json, PasswordEntity, find_server
from util.router import Router
from util.service import connect_via_ssh_with_password

router = Router()


@router.handle_arg(require_password=False)
def drop():
    """Reset the entire database by setting a new master password.

    Prompts the user to enter a new master password. The new password must
    be non-empty. Resets all stored data and encrypts the database with
    the new password.
    """
    new_master_pass = getpass('Enter new master password(all your data will be wiped): ')
    while len(new_master_pass) <= 0:
        new_master_pass = getpass('Master password cannot be 0 length, try again: ')
    encrypt_json(new_master_pass, [], get_salt())
    print('Database successfully dropped. New password set.')


@router.handle_arg()
def data(data, passwords):
    """Find and connect to a server using SSH based on provided data.

    Searches for the server using the provided 'data' and 'passwords' list.
    If the server is found, an SSH connection is established using the stored
    credentials.

    Args:
        data: The data used to identify the server.
        passwords: A list of PasswordEntity objects containing server credentials.
    """
    server = find_server(passwords, data)
    if server is not None:
        connect_via_ssh_with_password(server.ip_address, server.password, server.user)
    else:
        print('Server was not found')


@router.handle_arg()
def change(passwords):
    """Change the master password for the database.

    Prompts the user to enter a new master password, ensuring it is non-empty.
    Re-encrypts the existing password list with the new master password.

    Args:
        passwords: A list of PasswordEntity objects containing encrypted server credentials.
    """
    new_master_pass = getpass('Enter new master password: ')
    while len(new_master_pass) <= 0:
        new_master_pass = getpass('Master password cannot be 0 length, try again: ')
    encrypt_json(new_master_pass, passwords, get_salt())
    print('Master password successfully changed')


@router.handle_arg()
def add(ip_address, password, name, user, passwords, master_pass):
    """Add a new server to the list of saved passwords.

    Requires the IP address and password for the new server. If valid, adds a
    new PasswordEntity to the stored password list and re-encrypts it.

    Args:
        ip_address: The IP address of the server (IPv4/IPv6).
        password: The password to access the server.
        name: The name of the server.
        user: The username for accessing the server.
        passwords: A list of PasswordEntity objects containing server credentials.
        master_pass: The current master password for re-encrypting the database.
    """
    if not all([ip_address, password]):
        return print('To add a server, provide IP(4/6) and password')

    passwords.append(PasswordEntity(ip_address=ip_address, password=password, user=user, name=name))
    encrypt_json(master_pass, passwords, get_salt())
    print('Server successfully set:', f"IP:{ip_address}")