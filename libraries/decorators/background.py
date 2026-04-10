from functools import wraps
import threading


def background(daemon=False):
    """
    params:
    daemon = False: Non-daemon threads continue to run until they complete their execution,
    and they keep the program alive until all of these threads finish their tasks.
    The main program will wait for non-daemon threads to complete before it can terminate.

    daemon = True: Daemon threads are background threads that are killed automatically when the main program exits.
    They do not prevent the program from terminating.
    """

    def background(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            thread = threading.Thread(target=func, args=args, kwargs=kwargs)
            thread.daemon = daemon
            thread.start()
            return thread

        return wrapper

    return background