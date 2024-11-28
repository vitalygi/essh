from getpass import getpass
from typing import List
from util.data import PasswordEntity, decrypt_passwords, read_previous_term_session, write_term_session
from util.utils import create_function_with_counted_args, get_term_sid


class Router:
    def __init__(self):
        """Initialize the Router with a terminal session ID and context.

        The terminal session ID ensures unique identification across sessions.
        It also reads any previously saved master password for the terminal session.
        """
        self.term_session_id = get_term_sid()
        self.context = {
            'master_pass': read_previous_term_session(self.term_session_id)
        }
        self.handlers = dict()

    def handle_arg(self, arg=None, require_password: bool = True):
        """Decorator to handle argument-based function registration and execution.


        Args:
            arg (str, optional): The argument name to use for identifying the handler.
            require_password (bool, optional): If True, a password prompt will be invoked.
        """

        def decorate(fn):
            def wrapper(*args, **kwargs):
                if require_password:
                    self._ask_password_with_decryption()
                kwargs = self.context | kwargs
                new_function = create_function_with_counted_args(fn, *args, **kwargs)
                return new_function()

            self.handlers[arg or fn.__name__] = wrapper
            return wrapper

        return decorate

    def handle(self, *args, **kwargs):
        """Execute the appropriate handler based on the args and kwargs provided.

        The method checks the handlers dictionary and calls the corresponding
        registered function with the arguments if a match is found.
        """
        for arg in self.handlers.keys():
            val = kwargs.get(arg, None)
            if val is not None:
                return self.handlers[arg](*args, **kwargs)

    def _ask_password_with_decryption(self):
        """Prompt the user for a master password and decrypt stored passwords.

        If a master password already exists in the context, decrypt the passwords
        directly. Otherwise, prompt for the master password until a correct one
        is entered, then store the decrypted passwords into the context.
        """
        if self.context.get('master_pass', None) is not None:
            # Decrypt passwords if a master password exists
            self.context['passwords'] = decrypt_passwords(self.context.get('master_pass'))
        while True and self.context.get('passwords', None) is None:
            master_pass = getpass('Enter master password: ')
            if len(master_pass) == 0:
                print('Master password cannot be 0 length')
                continue
            else:
                passwords: List[PasswordEntity] = decrypt_passwords(master_pass)
                if passwords is not None:
                    # Store the validated master password and decrypted passwords
                    self.context['master_pass'] = master_pass
                    self.context['passwords'] = passwords
                    write_term_session(self.term_session_id, master_pass)
                    break