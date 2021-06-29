#!/usr/bin/env python3

import sys
from pathlib import Path
import logging
import argparse

from src.core import start


def init_logger():
    formatter = logging.Formatter('[%(asctime)s] {%(filename)s:%(lineno)d - %(name)s} %(levelname)s - %(message)s')
    Path("logs").mkdir(exist_ok=True)

    # set up log for this project (warn/debug/console)
    warn_file_handler = logging.FileHandler(filename='logs/logs_warn.log')
    warn_file_handler.setLevel(logging.WARN)
    warn_file_handler.setFormatter(formatter)
    debug_file_handler = logging.FileHandler(filename='logs/logs_debug.log')
    debug_file_handler.setLevel(logging.DEBUG)
    debug_file_handler.setFormatter(formatter)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.DEBUG)
    stderr_handler.setFormatter(formatter)
    # add handlers to the logger
    my_root = logging.getLogger('src')
    my_root.setLevel(logging.DEBUG)
    my_root.propagate = False
    my_root.addHandler(warn_file_handler)
    my_root.addHandler(debug_file_handler)
    my_root.addHandler(stderr_handler)

    # set up log for other modules (warn/console)
    warn_file_handler = logging.FileHandler(filename='logs/logs_modules_warn.log')
    warn_file_handler.setLevel(logging.WARN)
    warn_file_handler.setFormatter(formatter)
    # add handlers to the logger
    root = logging.getLogger('')
    root.setLevel(logging.INFO)
    root.addHandler(warn_file_handler)
    root.addHandler(stderr_handler)


if __name__ == '__main__':
    init_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", help="Custom settings.ini file")
    config_path = parser.parse_args().settings
    start.start(config_path=config_path)
