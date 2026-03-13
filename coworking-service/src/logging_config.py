from __future__ import annotations

import atexit
import logging
import logging.handlers
import queue
import sys

import structlog


def configure_logging(
    *,
    service_name: str,
    log_level: str = "INFO",
    loki_url: str = "",
) -> logging.handlers.QueueListener:
    level = getattr(logging, log_level.upper(), logging.INFO)

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    if loki_url and loki_url.strip():
        try:
            from logging_loki import LokiHandler

            handlers.append(
                LokiHandler(
                    url=f"{loki_url.rstrip('/')}/loki/api/v1/push",
                    tags={"service": service_name},
                    version="1",
                )
            )
        except Exception:  
            pass

    log_queue: queue.Queue[logging.LogRecord] = queue.Queue(-1)
    queue_handler = logging.handlers.QueueHandler(log_queue)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(queue_handler)

    listener = logging.handlers.QueueListener(
        log_queue, *handlers, respect_handler_level=True
    )
    listener.start()
    atexit.register(listener.stop)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    return listener
