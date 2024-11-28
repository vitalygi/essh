import os
import pexpect

def connect_via_ssh_with_password(ip, server_pass,user, port=22, clear=False):
    try:
        ssh_command = f"ssh {user}@{ip} -p {port}"
        child = pexpect.spawn(ssh_command)
        child.expect("password:")
        child.sendline(server_pass)
        if clear: os.system('cls' if os.name == 'nt' else 'clear')
        child.interact()
    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"SSH connection failed: {e}")