import logging
import sys

from core.settings import settings

formatter = logging.Formatter(fmt="%(asctime)s %(levelname)-8s %(message)s")

logger = logging.getLogger(__name__)
logger.setLevel(settings.logging_level)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
