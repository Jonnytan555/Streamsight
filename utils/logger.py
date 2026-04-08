import logging
import logging.handlers
import socket
import os
import sys

try:
    from concurrent_log_handler import ConcurrentRotatingFileHandler
    _has_concurrent = True
except ImportError:
    _has_concurrent = False


def setup_log(
        app: str,
        environment: str = None,
        minimum_level: int = logging.INFO,
        filename: str = None,
        backup_count: int = 10,
        alert_to: str = None,
        alert_minimum_level: int = logging.ERROR,
        rolling_max_bytes: int = 10 * 1024 * 1024,
        use_concurrent_file_handler: bool = True,
        use_stream: bool = False,
        smtp_host: str = None,
        smtp_port: int = 25,
        smtp_from: str = None,
):
    environment = environment or _get_environment()
    filename = filename or f"{app}.log"
    dirname = os.path.dirname(filename)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    log_format = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-8.8s] [%(filename)s:%(lineno)d] %(message)s"
    log_formatter = logging.Formatter(log_format)
    logging.basicConfig(level=minimum_level, format=log_format, handlers=[])

    root = logging.getLogger()

    if use_stream:
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(log_formatter)
        root.addHandler(stream_handler)

    if use_concurrent_file_handler and _has_concurrent:
        file_handler = ConcurrentRotatingFileHandler(
            filename=filename, backupCount=backup_count, maxBytes=rolling_max_bytes
        )
    else:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=filename, backupCount=backup_count, maxBytes=rolling_max_bytes
        )
    file_handler.setFormatter(log_formatter)
    root.addHandler(file_handler)

    if alert_to and smtp_host:
        root.addHandler(
            _get_smtp_handler(app, environment, alert_to, alert_minimum_level, smtp_host, smtp_port, smtp_from)
        )


def _get_smtp_handler(app, environment, alert_to, alert_minimum_level, smtp_host, smtp_port, smtp_from):
    from_addr = smtp_from or f"noreply@{smtp_host}"
    to_addrs = [e.strip() for e in alert_to.split(",")]
    handler = logging.handlers.SMTPHandler(
        mailhost=(smtp_host, smtp_port),
        fromaddr=from_addr,
        toaddrs=to_addrs,
        subject=f"[{environment}] Log Alert: {app}",
    )
    handler.setLevel(alert_minimum_level)
    return handler


def _get_environment() -> str:
    hostname = socket.gethostname().casefold()
    if hostname.startswith("prd"):
        return "Production"
    elif hostname.startswith("tst"):
        return "Test"
    else:
        return "Development"
