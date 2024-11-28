from getpass import getpass
from typing import List

from util.data import PasswordEntity, decrypt_passwords, read_previous_term_session, write_term_session
from util.utils import create_function_with_counted_args, get_term_sid


class Router:

    def __init__(self):
        self.term_session_id = get_term_sid()

        self.context = {
            'master_pass': read_previous_term_session(self.term_session_id)
        }
        self.handlers = dict()
        pass

    def handle_arg(self, arg=None, require_password: bool = True):
        def decorate(fn):
            def wrapper(*args, **kwargs):
                if require_password: self._ask_password_with_decryption()
                kwargs = self.context | kwargs
                new_function = create_function_with_counted_args(fn, *args, **kwargs)
                return new_function()

            self.handlers[arg or fn.__name__] = wrapper
            return wrapper

        return decorate

    def handle(self, *args, **kwargs):
        for arg in self.handlers.keys():
            val = kwargs.get(arg, None)
            if val is not None:
                return self.handlers[arg](*args, **kwargs)

    def _ask_password_with_decryption(self):
        if self.context.get('master_pass',None) is not None:
            self.context['passwords'] = decrypt_passwords(self.context.get('master_pass'))
        while True and self.context.get('passwords', None) is None:
            master_pass = getpass('Enter master password: ')
            if len(master_pass) == 0:
                print('Master password cannot be 0 length')
                continue
            else:
                passwords: List[PasswordEntity] = decrypt_passwords(master_pass)
            if passwords is not None:
                self.context['master_pass'] = master_pass
                self.context['passwords'] = passwords
                write_term_session(self.term_session_id,master_pass)
                break
