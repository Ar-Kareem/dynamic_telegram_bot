import sys
import logging

from src.core import start


def init_logger():
    warn_file_handler = logging.FileHandler(filename='logs/logs_warn.log')
    warn_file_handler.setLevel(logging.WARN)
    debug_file_handler = logging.FileHandler(filename='logs/logs_debug.log')
    debug_file_handler.setLevel(logging.DEBUG)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.DEBUG)
    handlers = [stderr_handler, debug_file_handler, warn_file_handler]

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] {%(filename)s:%(lineno)d - %(name)s} %(levelname)s - %(message)s',
        handlers=handlers
    )


if __name__ == '__main__':
    init_logger()
    start.start()
