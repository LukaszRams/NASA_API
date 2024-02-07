from logger import app_logger
import sys
from config import config

if __name__ == '__main__':
    app_logger.debug(f"App start with args: {sys.argv[1:]}")
