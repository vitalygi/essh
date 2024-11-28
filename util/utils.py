import inspect
from functools import partial
import subprocess
from contextlib import suppress
import hashlib
import psutil




def create_function_with_counted_args(fn, *args, **kwargs):
    spec = inspect.getfullargspec(fn)
    params = {*spec.args, *spec.kwonlyargs}
    kwargs = {k: kwargs[k] for k in params if k in kwargs}
    return partial(fn, *args, **kwargs)


def get_term_sid():
    tty = subprocess.run(['tty'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()
    pid = None
    proc_info = None
    for proc in psutil.process_iter(attrs=[]):
        with suppress(Exception):
            if proc.terminal() == tty:
                npid = min(pid or proc.pid,proc.pid)
                if pid != npid:
                    pid = npid
                    proc_info = proc.as_dict()

    create_time = proc_info.get('create_time','')
    ppid = proc_info.get('ppid', '')
    pid = proc_info.get('pid', '')
    name = proc_info.get('name', '')
    username = proc_info.get('username', '')
    return hashlib.sha256(f'{create_time}/{ppid}/{pid}/{name}/{username}/{tty}'.encode()).hexdigest()

