from functools import wraps
import logging
from time import time

def log(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        logging.info(f"Executing {f.__name__}...")
        start = time()
        result = f(*args, **kwargs)
        elapsed = time() - start
        logging.info(f"{f.__name__} completed in {elapsed:.2f}s")
        return result

    return wrapper