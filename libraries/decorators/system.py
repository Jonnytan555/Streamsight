import time
import psutil
import logging


def mem_threshold(
    max_percent: float = 90, wait_seconds: int = 2, timeout_seconds: int = 600
):
    def mem_threshold(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            while busy(
                "Memory",
                current_utilisation_percent=psutil.virtual_memory().percent,
                threshold_percent=max_percent,
            ) and not timedout(start_time, timeout_seconds):
                time.sleep(wait_seconds)
            if timedout(start_time, timeout_seconds):
                raise TimeoutError("Timedout. Server is busy.")
            return func(*args, **kwargs)

        return wrapper

    return mem_threshold


def cpu_threshold(
    max_percent: float = 90, wait_seconds: int = 2, timeout_seconds: int = 600
):
    def cpu_threshold(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            while busy(
                "CPU",
                current_utilisation_percent=psutil.cpu_percent(interval=0.1),
                threshold_percent=max_percent,
            ) and not timedout(start_time, timeout_seconds):
                time.sleep(wait_seconds)
            if timedout(start_time, timeout_seconds):
                raise TimeoutError("Timedout. Server is busy.")
            return func(*args, **kwargs)

        return wrapper

    return cpu_threshold


def timedout(start_time: int, timeout_seconds: int) -> bool:
    end_time = start_time + timeout_seconds
    if time.time() > end_time:
        return True
    return False


def busy(
    metric: str, current_utilisation_percent: float, threshold_percent: float
) -> bool:
    if current_utilisation_percent > threshold_percent:
        logging.info(
            f"Waiting... Reason: {metric} is above the threshold. Current usage: {current_utilisation_percent}, threshold: {threshold_percent}"
        )
        return True
    else:
        return False