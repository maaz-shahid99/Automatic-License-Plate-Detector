import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Create logs directory structure if it doesn't exist
LOGS_DIR = "logs/Application logs"
os.makedirs(LOGS_DIR, exist_ok=True)

# Log file paths
APP_LOG = os.path.join(LOGS_DIR, "app.log")
DETECTION_LOG = os.path.join(LOGS_DIR, "detection.log")
ERROR_LOG = os.path.join(LOGS_DIR, "error.log")

# Log format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def setup_logging():
    """Configure logging for the application"""
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)
    
    # ========== APP LOGGER (General application logs) ==========
    app_logger = logging.getLogger('app')
    app_logger.setLevel(logging.INFO)
    app_logger.handlers.clear()  # Clear existing handlers
    
    # App log file handler (10MB max, keep 5 backups)
    app_handler = RotatingFileHandler(
        APP_LOG, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(formatter)
    app_logger.addHandler(app_handler)
    
    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    app_logger.addHandler(console_handler)
    
    # ========== DETECTION LOGGER (License plate detections) ==========
    detection_logger = logging.getLogger('detection')
    detection_logger.setLevel(logging.INFO)
    detection_logger.handlers.clear()
    
    # Detection log file handler
    detection_handler = RotatingFileHandler(
        DETECTION_LOG,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    detection_handler.setLevel(logging.INFO)
    detection_handler.setFormatter(formatter)
    detection_logger.addHandler(detection_handler)
    
    # ========== ERROR LOGGER (Errors and exceptions) ==========
    error_logger = logging.getLogger('error')
    error_logger.setLevel(logging.ERROR)
    error_logger.handlers.clear()
    
    # Error log file handler
    error_handler = RotatingFileHandler(
        ERROR_LOG,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_logger.addHandler(error_handler)
    
    # Log startup message
    app_logger.info("="*60)
    app_logger.info("ALPR Toll Plaza System - Logging initialized")
    app_logger.info(f"Session started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    app_logger.info("="*60)
    
    return app_logger, detection_logger, error_logger

def get_logger(name='app'):
    """Get a logger by name"""
    return logging.getLogger(name)
