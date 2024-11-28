import os

import pexpect


def connect_via_ssh_with_password(ip, server_pass, user, port=22, clear=False):
    """Connect to a server via SSH using password authentication.

    Args:
        ip (str): The IP address of the server to connect to.
        server_pass (str): The password for the SSH user.
        user (str): The username to use for the SSH connection.
        port (int, optional): The SSH port (default is 22).
        clear (bool, optional): Whether to clear the terminal on successful connection.

    Note:
        Ensure `pexpect` is installed in the environment:
        `pip install pexpect`
    """
    try:
        ssh_command = f"ssh {user}@{ip} -p {port}"
        child = pexpect.spawn(ssh_command)
        child.expect("password:")
        child.sendline(server_pass)
        if clear:
            os.system('cls' if os.name == 'nt' else 'clear')
        child.interact()

    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"SSH connection failed: {e}")