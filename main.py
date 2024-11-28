import argparse
from handlers import router

parser = argparse.ArgumentParser(prog='SSH_Manager', description='Manage SSH server configurations securely.')
parser.add_argument('-a', '--add', help='Add a new server flag', action='store_true')
parser.add_argument('-ip', '--ip_address', help='IP(4/6) address of the server')
parser.add_argument('-p', '--password', help='Password for the server')
parser.add_argument('-n', '--name', help='Name of the server')
parser.add_argument('-d', '--drop', action='store_true', help='Drop existing database', default=None)
parser.add_argument('-u', '--user', help='User for server')
parser.add_argument('-c', '--change', action='store_true', help='Change master password flag', default=None)
parser.add_argument('data', help='Enter IP or name to connect to server', nargs='?', default=None)


def main():
    args = parser.parse_args()
    router.handle(**vars(args))


if __name__ == '__main__':
    main()
