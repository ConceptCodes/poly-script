import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("AuthService imported successfully!")
except Exception as e:
    logger.exception("Failed to import AuthService: %s", e)
    sys.exit(1)
