"""
Centralized logging configuration for the Discord Bot application.

This module provides a consistent logging setup across all services with:
- File rotation to prevent disk space issues
- Console output for development
- Structured formatting with timestamps and context
- Environment-based log levels
"""
# Not written by me all credit goes to claude code !

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Create logs directory if it doesn't exist
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log level from environment (default: INFO)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Log format with timestamp, level, module, and message
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance for a module.
    
    :param name: Name of the logger (typically __name__ of the calling module)
    :type name: str
    :return: Configured logger instance
    :rtype: logging.Logger
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(LOG_LEVEL)
        
        # Console handler for development
        console_handler = logging.StreamHandler()
        console_handler.setLevel(LOG_LEVEL)
        console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        
        # File handler with rotation (10MB max, keep 5 backup files)
        file_handler = RotatingFileHandler(
            LOG_DIR / 'discord_bot.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(LOG_LEVEL)
        file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        
        # Error file handler for errors only
        error_handler = RotatingFileHandler(
            LOG_DIR / 'discord_bot_errors.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
        error_handler.setFormatter(error_formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
    
    return logger


def log_function_call(logger: logging.Logger):
    """
    Decorator to log function calls with parameters and execution time.
    
    :param logger: Logger instance to use
    :type logger: logging.Logger
    :return: Decorator function
    """
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(f"Calling {func_name} with args={args[1:]} kwargs={kwargs}")
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                elapsed = (time.time() - start_time) * 1000
                logger.debug(f"{func_name} completed in {elapsed:.2f}ms")
                return result
            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                logger.error(f"{func_name} failed after {elapsed:.2f}ms: {str(e)}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            func_name = func.__name__
            logger.debug(f"Calling {func_name} with args={args[1:]} kwargs={kwargs}")
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = (time.time() - start_time) * 1000
                logger.debug(f"{func_name} completed in {elapsed:.2f}ms")
                return result
            except Exception as e:
                elapsed = (time.time() - start_time) * 1000
                logger.error(f"{func_name} failed after {elapsed:.2f}ms: {str(e)}")
                raise
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
