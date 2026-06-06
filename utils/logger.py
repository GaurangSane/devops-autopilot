import sys
from loguru import logger
from datetime import datetime
import os

# Remove default logger
logger.remove()

# Console logger — human readable during development
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# File logger — structured JSON for production
os.makedirs("logs", exist_ok=True)
logger.add(
    "logs/devops_autopilot_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message} | {extra}",
    level="DEBUG",
    rotation="1 day",       # New file every day
    retention="30 days",    # Keep 30 days of logs
    compression="zip",      # Compress old logs
    serialize=True          # Output as JSON — machine readable
)

def get_logger(name: str):
    """
    Returns a logger bound to a specific component name.
    Usage: logger = get_logger("log_analyzer")
    """
    return logger.bind(component=name)