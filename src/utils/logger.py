import logging
import sys

def setup_logger():
    # 1. Get the specific logger for your app
    logger = logging.getLogger("FireAndIceApp")

    # 2. Check if it's already configured. If so, just return it!
    # This stops the double-reporting dead in its tracks.
    if logger.handlers:
        return logger

    # 3. Configure the logger for the FIRST TIME only
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # Prevents sending logs to the root logger

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File Handler
    try:
        file_handler = logging.FileHandler('app_debug.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        pass # Fallback if file is locked

    # Stream Handler (Terminal)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # 4. Exception Hook
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

    return logger

# Create the singleton instance
log = setup_logger()