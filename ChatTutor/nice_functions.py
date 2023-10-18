import json


def pprint(*args):
    def wrapper(ob):
        if isinstance(ob, (str, int, float)):
            print(ob)

        elif isinstance(ob, dict):
            try:
                print(json.dumps(ob, indent=2, ensure_ascii=False))
            except:
                print(json.dumps(str(ob), indent=2, ensure_ascii=False))

        elif isinstance(ob, list):
            if any([True for el in ob if isinstance(el, (dict, list))]):
                for el in ob:
                    wrapper(el)
            else:
                print(ob)
        else:
            print(ob)        
    ''' Note: there exists also a package called pprint (from pprint import pprint)...'''

    if len(args) >= 2 and all([isinstance(el, (int, str, float)) for el in args]):
        print(bold(args[0]), *args[1:])
        return 
    elif len(args) == 2 and len(str(args[1])) < 50:
        print(bold(args[0]), str(args[1]))
        return 

    for i, el in enumerate(args): 
        # convert to bold if first elemenet
        if len(args)>1 and i==0 and isinstance(el, (int, str, float)):
            el = bold(el)
        wrapper(el)

def bold(some_string):
    """Convert to blue text"""
    return CBOLD + str(some_string) + CEND
def bold(some_string):
    """Convert to blue text"""
    return CBOLD + str(some_string) + CEND
def blue(some_string):
    """Convert to blue text"""
    return CBLUE + str(some_string) + CEND
def green(some_string):
    """Convert to green text"""
    return CGREEN + str(some_string) + CEND
def gray(some_string):
    """gray text"""
    return CGRAY + str(some_string) + CEND
def under(some_string):
    """under text"""
    return CUNDER + str(some_string) + CEND
def lgray(some_string):
    """light gray text"""
    return CLGRAY + str(some_string) + CEND
def red(some_string):
    """Convert to red text"""
    return CRED + str(some_string) + CEND
def white(some_string):
    """Convert to white text"""
    return CWHITE + str(some_string) + CEND
def yellow(some_string):
    """Convert to yellow text"""
    return CYELLOW + str(some_string) + CEND


# set print stdout to a given color
def set_to_color(color):
    if color == "blue":
        print(CBLUE, end="")
    if color == "green":
        print(CGREEN, end="")
    if color == "gray":
        print(CGRAY, end="")
    if color == "under":
        print(CUNDER, end="")
    if color == "lgray":
        print(CLGRAY, end="")
    elif color == "red":
        print(CRED, end="")
    elif color == "yellow":
        print(CYELLOW, end="")
    elif color == "white":
        print(CWHITE, end="")
    elif color == "end":
        print(CEND, end="")

# Print colors
CBLUE = '\033[94m'
CGREEN = '\033[92m'
CGRAY = '\033[90m'
CLGRAY = '\033[37m'
CRED = '\033[91m'
CWHITE = '\33[37m'
CYELLOW = '\33[33m'
CBOLD = '\033[1m'
CEND = '\033[0m'
CUNDER = '\033[4m'

import functools, time
def time_it(func):
    @functools.wraps(func)  # preserve information from original funct.
    def func_wrapper(*args, **kwargs):
        ts = time.time()
        result = func(*args, **kwargs)
        te = time.time()
        if 'log_time' in kwargs:
            name = kwargs.get('log_name', func.__name__.upper())
            kwargs['log_time'][name] = int((te - ts) * 1000)
        else:
            dt_s = (te - ts)  # in s
            dt_ms = (te - ts) * 1000  # in ms
            set_to_color("yellow")
            if dt_s < 1:
                print(f" -- execution time of function '{func.__name__}': {dt_ms:2.4f} ms --")
            else:
                print(f" -- execution time of function `{func.__name__}`: {dt_s:2.4f} s --")
            set_to_color("end")
        return result
    return func_wrapper