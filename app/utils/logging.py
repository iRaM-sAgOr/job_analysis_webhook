'''
Add logger instance and improve logging utility with clear function purposes

- Added a global `logger` instance for easy import across the app.
- Provided `setup_logging()` to configure logging format, level, and handlers.
- Provided `get_logger()` to get named loggers for modules.
- Each function and line is now clearly explained for maintainability.
'''


import logging  # Standard Python logging module
import sys      # For outputting logs to stdout

def setup_logging(log_level=logging.INFO):
    """
    Configures the logging system for the application.
    - log_level: Sets the minimum severity of logs to capture (default: INFO).
    - format: Specifies the log message format (timestamp, logger name, level, message).
    - handlers: 
        - StreamHandler(sys.stdout): Outputs logs to the console.
        - FileHandler('app.log'): Writes logs to 'app.log' file.
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),  # Console output
            logging.FileHandler('app.log')      # File output
        ]
    )
    logging.info("Logging is set up.")  # Log that logging is configured

def get_logger(name=None):
    """
    Returns a logger instance with the specified name.
    - name: The name of the logger (usually __name__ of the module).
    - If no name is provided, returns the root logger.
    """
    return logging.getLogger(name)

# Global logger instance for this module.
# Can be imported elsewhere as `from app.utils.logging import logger`
logger = get_logger(__name__)