import time
from threading import Thread

from src.utils import utils
from src.utils.affiliates import Store, Reducer


class Pocket:
    def __init__(self):
        self.store = Store()
        self.reducer = Reducer(store=self.store)
        self.config = utils.init_config()

        self.active_threads: list[Thread] = []
        self.inner_pocket: dict[str, any] = {}

        self.start_time = time.localtime()
        self.start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", self.start_time)
        self.telegram_updater = None

    def get(self, name: str) -> any:
        return self.inner_pocket.get(name)

    def set(self, name: str, value: any) -> None:
        self.inner_pocket[name] = value
