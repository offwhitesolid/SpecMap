"""
ErrorEngine - Centralized Error Handling and Logging System for SpecMap

This module provides a unified interface for error handling and logging across
the SpecMap application. It captures exceptions with full context, logs them
with detailed information, and displays user-friendly error messages.

Usage Examples:

    # Example 1: Using ErrorEngine as a context manager
    with error_engine.context("Loading spectrum file", filename=path):
        data = load_spectrum(path)

    # Example 2: Using ErrorEngine to handle exceptions
    try:
        result = risky_operation()
    except Exception as e:
        error_engine.handle_exception(e, context="User clicked Load button", severity="ERROR")

    # Example 3: Using ErrorEngine decorator
    @error_engine.track_errors(action="File save operation")
    def save_file(self, path):
        # implementation
        pass
"""

import logging
import traceback
import functools
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Callable

# Make tkinter optional for testing environments
try:
    from tkinter import messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    messagebox = None


class ErrorEngine:
    """
    Centralized error handling engine for SpecMap application.
    
    Provides logging, exception handling, and user notification functionality
    with full context tracking. Thread-safe for concurrent operations.
    
    Attributes:
        logger: Python logging.Logger instance
        context_data: Thread-local storage for context information
        show_messagebox: Whether to show GUI messageboxes for errors
    """
    
    def __init__(self, logger: logging.Logger, show_messagebox: bool = True):
        """
        Initialize the ErrorEngine.
        
        Args:
            logger: Configured Python logger instance
            show_messagebox: Whether to display error messageboxes (default: True)
        """
        self.logger = logger
        self.show_messagebox = show_messagebox
        self.context_data = threading.local()
        self._lock = threading.Lock()
    
    def _get_context(self) -> Dict[str, Any]:
        """Get thread-local context data."""
        if not hasattr(self.context_data, 'stack'):
            self.context_data.stack = []
        return self.context_data.stack
    
    def handle_exception(
        self,
        exception: Exception,
        context: str = "",
        severity: str = "ERROR",
        show_user_message: bool = True,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Handle an exception with full context logging.
        
        Args:
            exception: The exception that was raised
            context: Description of what was being done when error occurred
            severity: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            show_user_message: Whether to show messagebox to user
            additional_info: Additional context information (file path, user action, etc.)
        
        Example:
            try:
                load_file(path)
            except Exception as e:
                error_engine.handle_exception(
                    e,
                    context="Loading spectrum file",
                    additional_info={"filename": path, "user_action": "Load button clicked"}
                )
        """
        # Build comprehensive error message
        error_type = type(exception).__name__
        error_msg = str(exception)
        
        # Get stack trace
        tb_str = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        
        # Get context stack
        context_stack = self._get_context()
        
        # Build log message
        log_parts = []
        
        if context:
            log_parts.append(f"Context: {context}")
        
        if context_stack:
            log_parts.append(f"Context Stack: {' -> '.join(context_stack)}")
        
        log_parts.append(f"Error Type: {error_type}")
        log_parts.append(f"Error Message: {error_msg}")
        
        if additional_info:
            info_str = ", ".join([f"{k}={v}" for k, v in additional_info.items()])
            log_parts.append(f"Additional Info: {info_str}")
        
        log_parts.append(f"Traceback:\n{tb_str}")
        
        full_log_message = "\n".join(log_parts)
        
        # Log with appropriate severity
        log_level = getattr(logging, severity.upper(), logging.ERROR)
        self.logger.log(log_level, full_log_message)
        
        # Show user-friendly message if requested
        if show_user_message and self.show_messagebox:
            user_message = self._create_user_message(error_type, error_msg, context)
            try:
                if TKINTER_AVAILABLE and messagebox:
                    messagebox.showerror("Error", user_message)
                else:
                    # Fallback to console if tkinter not available
                    print(f"\n{'='*60}\nERROR: {user_message}\n{'='*60}\n")
            except Exception as e:
                # If messagebox fails, just log it
                self.logger.warning(f"Failed to show error messagebox: {e}")
    
    def _create_user_message(self, error_type: str, error_msg: str, context: str) -> str:
        """
        Create a user-friendly error message.
        
        Args:
            error_type: Type of the exception
            error_msg: Exception message
            context: Context description
            
        Returns:
            User-friendly error message string
        """
        parts = []
        
        if context:
            parts.append(f"An error occurred while: {context}")
        else:
            parts.append("An error occurred")
        
        # Add specific error info
        parts.append(f"\nError: {error_msg}")
        
        # Add helpful hint based on error type
        if "FileNotFoundError" in error_type or "No such file" in error_msg:
            parts.append("\nPlease check that the file path is correct and the file exists.")
        elif "PermissionError" in error_type:
            parts.append("\nPlease check that you have permission to access this file.")
        elif "pickle" in error_msg.lower():
            parts.append("\nThe save file may be corrupted or from an incompatible version.")
        
        parts.append("\nCheck the log file for more details.")
        
        return "\n".join(parts)
    
    def context(self, description: str, **kwargs):
        """
        Context manager for tracking operation context.
        
        Args:
            description: Description of the operation
            **kwargs: Additional context information to log
            
        Example:
            with error_engine.context("Loading spectrum file", filename=path):
                data = load_spectrum(path)
        """
        return ErrorContext(self, description, kwargs)
    
    def track_errors(self, action: str, show_user_message: bool = True):
        """
        Decorator for automatic error handling.
        
        Args:
            action: Description of the action being performed
            show_user_message: Whether to show messagebox on error
            
        Example:
            @error_engine.track_errors(action="File save operation")
            def save_file(self, path):
                # implementation
                pass
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    # Extract additional info from args if possible
                    additional_info = {
                        "function": func.__name__,
                        "module": func.__module__
                    }
                    
                    # Try to get filename/path from common parameter names
                    for arg_name in ['filename', 'path', 'filepath', 'file']:
                        if arg_name in kwargs:
                            additional_info[arg_name] = kwargs[arg_name]
                            break
                    
                    self.handle_exception(
                        e,
                        context=action,
                        show_user_message=show_user_message,
                        additional_info=additional_info
                    )
                    raise  # Re-raise to maintain existing behavior
            return wrapper
        return decorator
    
    def log_info(self, message: str, **kwargs):
        """
        Log an informational message with optional context.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        if kwargs:
            info_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            message = f"{message} [{info_str}]"
        self.logger.info(message)
    
    def log_warning(self, message: str, **kwargs):
        """
        Log a warning message with optional context.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        if kwargs:
            info_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            message = f"{message} [{info_str}]"
        self.logger.warning(message)
    
    def log_debug(self, message: str, **kwargs):
        """
        Log a debug message with optional context.
        
        Args:
            message: The message to log
            **kwargs: Additional context information
        """
        if kwargs:
            info_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            message = f"{message} [{info_str}]"
        self.logger.debug(message)


class ErrorContext:
    """
    Context manager for ErrorEngine that tracks nested operation contexts.
    """
    
    def __init__(self, engine: ErrorEngine, description: str, kwargs: Dict[str, Any]):
        """
        Initialize the error context.
        
        Args:
            engine: The ErrorEngine instance
            description: Description of the operation
            kwargs: Additional context information
        """
        self.engine = engine
        self.description = description
        self.kwargs = kwargs
    
    def __enter__(self):
        """Enter the context, adding to context stack."""
        context_stack = self.engine._get_context()
        context_stack.append(self.description)
        
        # Log entry if there's additional info
        if self.kwargs:
            info_str = ", ".join([f"{k}={v}" for k, v in self.kwargs.items()])
            self.engine.logger.debug(f"Starting: {self.description} [{info_str}]")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context, removing from context stack and handling any exception."""
        context_stack = self.engine._get_context()
        if context_stack:
            context_stack.pop()
        
        if exc_type is not None:
            # An exception occurred, handle it
            self.engine.handle_exception(
                exc_val,
                context=self.description,
                additional_info=self.kwargs
            )
            # Return False to propagate the exception
            return False
        
        return True


def setup_logger(
    name: str = "SpecMap",
    log_dir: str = "logs",
    max_bytes: int = 5 * 1024 * 1024,  # 5MB
    backup_count: int = 5,
    level: int = logging.DEBUG
) -> logging.Logger:
    """
    Set up a logger with rotating file handler.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        max_bytes: Maximum size per log file (default: 5MB)
        backup_count: Number of backup files to keep (default: 5)
        level: Logging level (default: DEBUG)
        
    Returns:
        Configured logger instance
        
    Example:
        logger = setup_logger("SpecMap", "logs")
        error_engine = ErrorEngine(logger)
    """
    from logging.handlers import RotatingFileHandler
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid adding duplicate handlers
    if logger.handlers:
        return logger
    
    # Create rotating file handler
    log_file = log_path / f"{name.lower()}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    
    # Create console handler for warnings and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
    # Create formatter
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(module)s:%(funcName)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Module-level convenience functions for easy access
_default_engine: Optional[ErrorEngine] = None


def initialize_error_engine(logger: Optional[logging.Logger] = None, show_messagebox: bool = True) -> ErrorEngine:
    """
    Initialize the global error engine instance.
    
    Args:
        logger: Logger instance (will create default if None)
        show_messagebox: Whether to show GUI messageboxes
        
    Returns:
        ErrorEngine instance
    """
    global _default_engine
    
    if logger is None:
        logger = setup_logger()
    
    _default_engine = ErrorEngine(logger, show_messagebox)
    return _default_engine


def get_error_engine() -> ErrorEngine:
    """
    Get the global error engine instance.
    
    Returns:
        ErrorEngine instance
        
    Raises:
        RuntimeError: If error engine not initialized
    """
    global _default_engine
    
    if _default_engine is None:
        raise RuntimeError("ErrorEngine not initialized. Call initialize_error_engine() first.")
    
    return _default_engine
