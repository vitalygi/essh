import inspect
from functools import partial


def create_function_with_counted_args(fn,*args,**kwargs):
    spec = inspect.getfullargspec(fn)
    params = {*spec.args, *spec.kwonlyargs}
    kwargs = {k: kwargs[k] for k in params if k in kwargs}
    return partial(fn, *args, **kwargs)




