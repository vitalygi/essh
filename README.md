# Easy SSH (essh)

Welcome to **Easy SSH**, a Python-based command-line tool for managing and storing SSH server configurations securely. This tool simplifies the process of connecting to multiple SSH servers by allowing users to store server credentials and connect to them seamlessly using a master password.

## Features

- **Secure Storage**: Stores SSH server details encrypted with a master password using PBKDF2 and Fernet cryptography.
- **Connect Seamlessly**: Quickly connect to your SSH servers using stored credentials.
- **Command Line Interface (CLI)**: Easy to use command-line options for adding new servers, connecting, and changing the master password.
- **IP Address and Name Support**: Fetch server details using either the server's IP address or a custom name.
- **Terminal sessions support** You do not need to re-enter master password in same terminal session (working for 1 instance).

## Installation

```bash
# Clone the repository
git clone https://github.com/vitalygi/essh.git

# Navigate into the directory
cd essh

# Install the required Python packages
pip install -r requirements.txt
```

## Usage

After installing `Easy SSH`, you can use the following commands:

1. **Add a Server**

   To add a new SSH server configuration:

   ```bash
   python ssh.py --add --ip_address [SERVER_IP] --password [SERVER_PASSWORD] --name [SERVER_NAME] --user [USERNAME]
   ```

   - `--ip_address`: IP address of the server.
   - `--password`: Password for the server.
   - `--name`: Optional custom name for the server.
   - `--user`: Optional username to connect with (defaults to `root`).

2. **Connect to a Server**

   To connect to an SSH server:

   ```bash
   python ssh.py [SERVER_IP_OR_NAME]
   ```

3. **Change Master Password**

   To change the master password for encrypted data:

   ```bash
   python ssh.py --change
   ```

## Master Password

The script uses a master password, which is required to encrypt and decrypt your server details. During the initial setup, you enter this password.

**Note**: A default master password is used if no input is provided at the prompt. It's highly recommended to set a strong master password.

## Security

- Encrypted using PBKDF2 HMAC with SHA-256.
- Data integrity and confidentiality are ensured through Fernet symmetric encryption.


## Contributions

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.
