"""
Silent Output Module
Utilities for suppressing output during initialization and execution
"""

import sys
import os
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from io import StringIO


@contextmanager
def suppress_prints():
    """
    Context manager to suppress all stdout and stderr output.
    """
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        try:
            sys.stdout = devnull
            sys.stderr = devnull
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


def silent_execution(func, *args, **kwargs):
    """
    Execute a function silently, suppressing all output.
    
    Args:
        func: Function to execute
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
    
    Returns:
        The return value of the function, or None if an exception occurred
    """
    try:
        with suppress_prints():
            return func(*args, **kwargs)
    except Exception:
        # Silently handle any exceptions
        return None


@contextmanager
def capture_output():
    """
    Context manager to capture stdout and stderr output.
    
    Returns:
        tuple: (stdout_content, stderr_content)
    """
    stdout_capture = StringIO()
    stderr_capture = StringIO()
    
    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        yield stdout_capture, stderr_capture


def suppress_warnings():
    """
    Suppress various warning outputs.
    """
    import warnings
    warnings.filterwarnings("ignore")
    
    # Suppress specific library warnings
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    # Suppress TensorFlow warnings if available
    try:
        import tensorflow as tf
        tf.get_logger().setLevel('ERROR')
    except ImportError:
        pass
    
    # Suppress PyTorch warnings if available
    try:
        import torch
        torch.set_warn_always(False)
    except ImportError:
        pass


class SilentLogger:
    """
    A logger that does nothing - used to replace noisy loggers.
    """
    def debug(self, *args, **kwargs):
        pass
    
    def info(self, *args, **kwargs):
        pass
    
    def warning(self, *args, **kwargs):
        pass
    
    def error(self, *args, **kwargs):
        pass
    
    def critical(self, *args, **kwargs):
        pass
    
    def setLevel(self, level):
        pass


def make_logger_silent(logger_name):
    """
    Replace a logger with a silent version.
    
    Args:
        logger_name (str): Name of the logger to silence
    """
    import logging
    logging.getLogger(logger_name).setLevel(logging.ERROR)