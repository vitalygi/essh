import inspect
from functools import partial
import subprocess
from contextlib import suppress
import hashlib
import psutil


def create_function_with_counted_args(fn, *args, **kwargs):
    """Create a partial function with arguments limited to those required by the function.

    This function uses `inspect` to get the argument specification of the
    provided function `fn`. It then prepares a `partial` function, including
    only the arguments specified by `fn`.

    Args:
        fn: The function to partially apply.
        *args: The positional arguments to count for the partial application.
        **kwargs: The keyword arguments to count for the partial application.

    Returns:
        A callable `partial` object with the applied arguments.
    """
    spec = inspect.getfullargspec(fn)
    params = {*spec.args, *spec.kwonlyargs}
    kwargs = {k: kwargs[k] for k in params if k in kwargs}
    return partial(fn, *args, **kwargs)


def get_term_sid():
    """Generate a session identifier based on terminal and process information.

    This function retrieves the terminal name using the `tty` command and then
    iterates over all running processes to find processes attached to the same
    terminal. It collects specific attributes of the process to create a unique
    SHA-256 hash representing the session ID.

    Returns:
        A SHA-256 hash string that acts as a unique session identifier.
    """
    # Get the terminal name
    tty = subprocess.run(['tty'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()

    pid = None
    proc_info = None

    # Iterate over all processes to find the process associated with the terminal
    for proc in psutil.process_iter(attrs=[]):
        with suppress(Exception):
            if proc.terminal() == tty:
                # Select process with the minimum PID that has the same terminal
                npid = min(pid or proc.pid, proc.pid)
                if pid != npid:
                    pid = npid
                    proc_info = proc.as_dict()

    # Gather process details
    create_time = proc_info.get('create_time', '')
    ppid = proc_info.get('ppid', '')
    pid = proc_info.get('pid', '')
    name = proc_info.get('name', '')
    username = proc_info.get('username', '')

    # Generate SHA-256 hash based on collected information
    session_id_str = f'{create_time}/{ppid}/{pid}/{name}/{username}/{tty}'
    return hashlib.sha256(session_id_str.encode()).hexdigest()