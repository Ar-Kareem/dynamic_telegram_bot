from threading import Thread
from typing import Any

from configparser import ConfigParser
from telegram.ext import Updater

from src.utils import utils
from src.utils.affiliates import Store, Reducer


class Pocket:
    def __init__(self):
        self.store: Store
        self.reducer: Reducer
        self.config: ConfigParser
        self.bot: Updater
        self.active_threads: list[Thread] = []
        self.inner_pocket: dict[str, Any] = {}


def main():
    r = utils.get_all_scripts(function_name_check='init')
    print(r)
