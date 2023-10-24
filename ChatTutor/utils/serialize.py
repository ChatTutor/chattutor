import re
from copy import deepcopy


def serialize(func):
    import inspect
    lines = inspect.getsource(func)    
    return lines

def serialize_iteratively (object):
    """transforms all callables to string"""
    def iteration(object):
        if object.__class__ ==re.Pattern:
            return object.pattern
        if callable(object):
            return serialize(object)
        if isinstance(object, list):
            return [iteration(el) for el in object]
        if isinstance(object, dict):
            for key, value in object.copy().items():
                object[key] = iteration(value)
            return object
        return object

    # copy dict and perform operation
    copied_object = deepcopy(object)
    return iteration(copied_object)