###
# logging_config.py
# This file configures centralized logging for the OSSL2Gif application.
# Version 2.0.0 © 2026 by Manfred Zainhofer
###

import logging
import logging.handlers
import os
import sys

def setup_logging(log_level: int = logging.INFO) -> logging.Logger:
    """
    Configures centralized logging for the application.
    
    Args:
        log_level: The logging level (default: logging.INFO)
    
    Returns:
        A logger instance for use in the application
    """
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure log file path
    if getattr(sys, 'frozen', False):
        # In PyInstaller bundle
        log_file = os.path.join(os.getcwd(), log_dir, 'ossl2gif.log')
    else:
        # In normal Python environment
        log_file = os.path.join(os.path.dirname(__file__), log_dir, 'ossl2gif.log')
    
    # Create logger
    logger = logging.getLogger('OSSL2Gif')
    logger.setLevel(log_level)
    
    # Prevent duplicate handlers if setup_logging is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation (10MB, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler for console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger instance for a specific module.
    
    Args:
        name: The module name (typically __name__)
    
    Returns:
        A logger instance
    """
    return logging.getLogger(name)
