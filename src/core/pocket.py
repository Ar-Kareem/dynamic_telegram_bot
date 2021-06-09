from typing import Dict

from src.utils import utils
from src.utils.affiliates import Store, Reducer


class Pocket:
    def __init__(self, config_path=None):
        self.store = Store()
        self.reducer = Reducer(store=self.store)
        self.config = utils.init_config(config_path=config_path)
        self.database_dir = utils.get_db_path()

        self.inner_pocket: Dict[str, any] = {}
        self.telegram_updater = None

    def get(self, name: str) -> any:
        return self.inner_pocket.get(name)

    def set(self, name: str, value: any) -> None:
        self.inner_pocket[name] = value
