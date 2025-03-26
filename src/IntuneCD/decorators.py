# -*- coding: utf-8 -*-
import time
import os

DEBUG = os.environ.get("DEBUG", False)


def time_command():
    def wrapper(func):
        def wrapped(*args, **kwargs):
            if not DEBUG:
                return func(*args, **kwargs)
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"[DEBUG] {func.__name__} ran in: {round(end - start)} seconds")
            return result

        return wrapped

    return wrapper
