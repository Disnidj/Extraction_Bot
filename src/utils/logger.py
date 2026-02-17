# src/utils/logger.py
import logging
import os
import glob
from datetime import datetime
from src.utils.load_yaml import LOGS_PATH

# Ensure the directory exists
os.makedirs(LOGS_PATH, exist_ok=True)

# Global variable to store current request ID for logging context
_current_request_id = None

def clear_all_logs():
    """Clear all log files in the logs directory before starting a new run."""
    try:
        log_files = glob.glob(os.path.join(LOGS_PATH, "*.log"))
        for log_file in log_files:
            try:
                # Truncate the file (clear content but keep the file)
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write("")
                print(f"✓ Cleared: {os.path.basename(log_file)}")
            except Exception as e:
                print(f"⚠️  Could not clear {os.path.basename(log_file)}: {e}")
        print(f"📋 Cleared {len(log_files)} log file(s)\n")
    except Exception as e:
        print(f"❌ Error clearing logs: {e}")

def set_current_request_id(request_id):
    """Set the current request ID for logging context."""
    global _current_request_id
    _current_request_id = request_id

def get_current_request_id():
    """Get the current request ID for logging context."""
    return _current_request_id

# Common formatter used by all handlers (created at module level)
COMMON_FORMATTER = logging.Formatter(
    "{asctime} - {levelname} - {filename}:{lineno} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M"
)

# Portal-specific formatter for Issues log to clearly identify which portal the issue is from
ISSUES_FORMATTER = logging.Formatter(
    "{asctime} - {levelname} - [REQ:{request_id}] - [{name}] - {filename}:{lineno} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M"
)

class CustomLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        # Add current request ID to the logging record
        extra["request_id"] = get_current_request_id() or "UNKNOWN"
        kwargs["extra"] = extra
        return msg, kwargs

def _create_logger(portal_name):
    """
    Creates and returns a logger specific to the given portal
    
    Args:
        portal_name (str): Name of the portal (e.g., 'ngi', 'takaful')
        
    Returns:
        CustomLoggerAdapter: Logger adapter configured for the specified portal
    """
    # Create a log file path for this portal
    log_file = os.path.join(LOGS_PATH, f"{portal_name}.log")
    
    # Create a logger with the portal name
    portal_logger = logging.getLogger(portal_name)
    
    # Clear any existing handlers to avoid duplicate logs
    if portal_logger.handlers:
        portal_logger.handlers.clear()
    
    # Set log level
    portal_logger.setLevel(logging.DEBUG)
    
    # Create file handler for this portal with errors='replace' to handle any Unicode issues
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8', errors='replace')
    
    # Set formatter
    file_handler.setFormatter(COMMON_FORMATTER)
    
    # Add handler to logger
    portal_logger.addHandler(file_handler)

    # Console handler removed to keep terminal clean - logs only go to files
    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(COMMON_FORMATTER)
    # portal_logger.addHandler(console_handler)
    
    # Set propagation to False to prevent duplicate logs
    portal_logger.propagate = False
    
    # Return a CustomLoggerAdapter for this portal logger
    return CustomLoggerAdapter(portal_logger, {})

logger = _create_logger("app")

# Custom filter to only allow specific issue messages in Issues.log
class IssuesFilter(logging.Filter):
    def filter(self, record):
        # Allow request start/completion messages
        if hasattr(record, 'msg') and record.msg:
            msg_str = str(record.msg)
            if ("Starting processing for Request" in msg_str or 
                "processing completed successfully" in msg_str):
                return True
            
            # Allow final issue summary messages
            if ("Failed fields:" in msg_str or 
                "Error:" in msg_str or
                "❌" in msg_str):
                return True
        
        # Filter out all other messages
        return False

# Create a shared Issues handler that logs WARNING and ERROR to a central file
issues_file = os.path.join(LOGS_PATH, "Issues.log")
issues_handler = logging.FileHandler(issues_file, mode='a', encoding='utf-8', errors='replace')
issues_handler.setLevel(logging.WARNING)
issues_handler.addFilter(IssuesFilter())
issues_handler.setFormatter(ISSUES_FORMATTER)

# Create a dedicated issues logger that only writes to Issues.log
def _create_issues_logger():
    """Create a dedicated logger for issues that only writes to Issues.log."""
    issues_logger = logging.getLogger("issues")
    issues_logger.setLevel(logging.WARNING)
    
    # Clear any existing handlers
    if issues_logger.handlers:
        issues_logger.handlers.clear()
    
    # Only add the Issues handler (no file handler, no console handler)
    issues_logger.addHandler(issues_handler)
    
    # Set propagation to False
    issues_logger.propagate = False
    
    return CustomLoggerAdapter(issues_logger, {})

issues_logger = _create_issues_logger()

# Create main execution logger for overall flow tracking
def _create_main_execution_logger():
    """Create a dedicated logger for main execution flow and timing."""
    main_log_file = os.path.join(LOGS_PATH, "main_execution.log")
    main_logger = logging.getLogger("main_execution")
    main_logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    if main_logger.handlers:
        main_logger.handlers.clear()
    
    # Create file handler with errors='replace' to support Unicode/emojis
    file_handler = logging.FileHandler(main_log_file, mode='a', encoding='utf-8', errors='replace')
    file_handler.setFormatter(COMMON_FORMATTER)
    main_logger.addHandler(file_handler)
    
    # Add console handler for main execution to show timing info
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(COMMON_FORMATTER)
    main_logger.addHandler(console_handler)
    
    main_logger.propagate = False
    return CustomLoggerAdapter(main_logger, {})

main_execution_logger = _create_main_execution_logger()

# Pre-create loggers for each portal so they can be imported directly
alsagr_logger = _create_logger("alsagr")
adnic_logger = _create_logger("adnic")
dni_logger = _create_logger("dni")
dubaiinsurance_logger = _create_logger("dubaiinsurance")
ison_logger = _create_logger("ison")
maxhealth_logger = _create_logger("maxhealth")
nlg_logger = _create_logger("nlg")
qatar_logger = _create_logger("qatar")
sukoon_logger = _create_logger("sukoon")
takaful_logger = _create_logger("takaful")
# union_logger = _create_logger("union")
orient_logger = _create_logger("orient")
orient_aura_logger = _create_logger("orient_aura")
rak_logger = _create_logger("rak")
fidelity_logger = _create_logger("fidelity")
# salama_logger = _create_logger("salama")
wataniatakaful_logger = _create_logger("wataniatakaful")
medgulf_logger = _create_logger("medgulf")
alittihad_logger = _create_logger("alittihad")
daman_logger = _create_logger("daman")
gig_logger = _create_logger("gig")

# Attach the Issues handler to all existing portal loggers
for _logger in [
    alsagr_logger, adnic_logger, dni_logger, dubaiinsurance_logger,
    ison_logger, maxhealth_logger, nlg_logger, qatar_logger, sukoon_logger,
    takaful_logger, orient_logger, orient_aura_logger, rak_logger, fidelity_logger, 
    wataniatakaful_logger, medgulf_logger, alittihad_logger, daman_logger, gig_logger
]:
    try:
        # underlying logger is LoggerAdapter, get the actual logger object
        base_logger = _logger.logger if hasattr(_logger, 'logger') else _logger
        # avoid duplicate handler addition
        if not any(isinstance(h, logging.FileHandler) and getattr(h, 'baseFilename', '') == issues_file for h in base_logger.handlers):
            base_logger.addHandler(issues_handler)
    except Exception:
        # ignore any issues while attaching handlers
        pass