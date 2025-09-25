import logging

def setup_logger():
    """Set up the logger for the application."""
    logger = logging.getLogger('health_symptom_checker')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler('user_interactions.log')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
