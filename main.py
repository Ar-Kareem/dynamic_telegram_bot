#!/usr/bin/env python3

import argparse
from src.core import start

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", help="Custom settings.ini file")
    config_path = parser.parse_args().settings
    start.start(config_path=config_path)
