import logging


def setup_logger() -> logging.Logger:
    """Configure and return the application logger."""
    logger = logging.getLogger("read-audio")
    logger.setLevel(logging.INFO)

    # Console handler
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(message)s"
    )  # Simple format for user-facing messages
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = setup_logger()
