"""
Logging utilities for SafeErase Python UI
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    from loguru import logger as loguru_logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False

class SafeEraseLogger:
    """Custom logger for SafeErase application"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = None
        self._setup_logger()
        
    def _setup_logger(self):
        """Set up the logger"""
        if LOGURU_AVAILABLE:
            self._setup_loguru()
        else:
            self._setup_standard_logging()
            
    def _setup_loguru(self):
        """Set up loguru logger"""
        # Remove default handler
        loguru_logger.remove()
        
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Console handler
        loguru_logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level="INFO",
            colorize=True
        )
        
        # File handler
        loguru_logger.add(
            log_dir / "safeerase_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="DEBUG",
            rotation="1 day",
            retention="30 days",
            compression="zip"
        )
        
        # Error file handler
        loguru_logger.add(
            log_dir / "safeerase_errors_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="ERROR",
            rotation="1 day",
            retention="90 days",
            compression="zip"
        )
        
        self.logger = loguru_logger.bind(name=self.name)
        
    def _setup_standard_logging(self):
        """Set up standard Python logging"""
        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
            
        # Console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler(
            log_dir / f"safeerase_{datetime.now().strftime('%Y-%m-%d')}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.FileHandler(
            log_dir / f"safeerase_errors_{datetime.now().strftime('%Y-%m-%d')}.log"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        self.logger.addHandler(error_handler)
        
    def debug(self, message: str, *args, **kwargs):
        """Log debug message"""
        if LOGURU_AVAILABLE:
            self.logger.debug(message, *args, **kwargs)
        else:
            self.logger.debug(message, *args, **kwargs)
            
    def info(self, message: str, *args, **kwargs):
        """Log info message"""
        if LOGURU_AVAILABLE:
            self.logger.info(message, *args, **kwargs)
        else:
            self.logger.info(message, *args, **kwargs)
            
    def warning(self, message: str, *args, **kwargs):
        """Log warning message"""
        if LOGURU_AVAILABLE:
            self.logger.warning(message, *args, **kwargs)
        else:
            self.logger.warning(message, *args, **kwargs)
            
    def error(self, message: str, *args, **kwargs):
        """Log error message"""
        if LOGURU_AVAILABLE:
            self.logger.error(message, *args, **kwargs)
        else:
            self.logger.error(message, *args, **kwargs)
            
    def critical(self, message: str, *args, **kwargs):
        """Log critical message"""
        if LOGURU_AVAILABLE:
            self.logger.critical(message, *args, **kwargs)
        else:
            self.logger.critical(message, *args, **kwargs)
            
    def exception(self, message: str, *args, **kwargs):
        """Log exception with traceback"""
        if LOGURU_AVAILABLE:
            self.logger.exception(message, *args, **kwargs)
        else:
            self.logger.exception(message, *args, **kwargs)

# Global logger instances
_loggers = {}

def setup_logger(name: str) -> SafeEraseLogger:
    """Set up and return a logger instance"""
    if name not in _loggers:
        _loggers[name] = SafeEraseLogger(name)
    return _loggers[name]

def get_logger(name: str) -> SafeEraseLogger:
    """Get an existing logger instance"""
    if name not in _loggers:
        return setup_logger(name)
    return _loggers[name]

def configure_logging(level: str = "INFO", log_dir: Optional[str] = None):
    """Configure global logging settings"""
    if log_dir:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
    # Set global log level
    if LOGURU_AVAILABLE:
        loguru_logger.remove()
        
        # Console handler with specified level
        loguru_logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan> | "
                   "<level>{message}</level>",
            level=level.upper(),
            colorize=True
        )
        
        # File handler
        if log_dir:
            loguru_logger.add(
                Path(log_dir) / "safeerase_{time:YYYY-MM-DD}.log",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} | {message}",
                level="DEBUG",
                rotation="1 day",
                retention="30 days"
            )
    else:
        # Configure standard logging
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

def log_performance(func):
    """Decorator to log function performance"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = datetime.now()
        
        try:
            result = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            logger.debug(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
            
    return wrapper

def log_async_performance(func):
    """Decorator to log async function performance"""
    import asyncio
    
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = datetime.now()
        
        try:
            result = await func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            logger.debug(f"{func.__name__} completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise
            
    return wrapper

class LogContext:
    """Context manager for logging with additional context"""
    
    def __init__(self, logger: SafeEraseLogger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
        
    def __enter__(self):
        self.start_time = datetime.now()
        context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
        self.logger.info(f"Starting {self.operation}" + (f" ({context_str})" if context_str else ""))
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        if exc_type is None:
            self.logger.info(f"Completed {self.operation} in {duration:.3f}s")
        else:
            self.logger.error(f"Failed {self.operation} after {duration:.3f}s: {exc_val}")
            
        return False  # Don't suppress exceptions

# Example usage:
# logger = get_logger("MyModule")
# with LogContext(logger, "device discovery", device_count=5):
#     # perform operation
#     pass
