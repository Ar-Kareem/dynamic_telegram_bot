from threading import Thread
from typing import Any
import logging

from src.core.actions import TelegramBotInitiated, InitScriptsFinished, Terminate
from src.utils import utils
from src.utils.affiliates import Store, Reducer

logger = logging.getLogger(__name__)


class Pocket:
    def __init__(self):
        self.store = Store()
        self.reducer = Reducer(store=self.store)
        self.config = utils.init_config()
        self.active_threads: list[Thread] = []
        self.inner_pocket: dict[str, Any] = {}
        self.telegram_updater = None

    def register_bot(self, telegram_updater):
        self.telegram_updater = telegram_updater
        self.store.dispatch(TelegramBotInitiated())

    def get(self, name: str) -> Any:
        return self.inner_pocket.get(name)

    def set(self, name: str, value: Any) -> None:
        self.inner_pocket[name] = value


def init_scripts(pocket: Pocket):
    scripts = utils.get_all_scripts(function_name_check='init')
    for script in scripts:
        # noinspection PyBroadException
        try:
            script.init(pocket)
        except Exception:
            logger.exception('Exception in dynamic init for script ' + script.__name__ + '.py"')
    pocket.store.dispatch(InitScriptsFinished())


def reducer_loop(pocket: Pocket):
    try:
        last_action: Terminate = pocket.reducer.start(stop_action=Terminate)
        if last_action.reset_flag:
            Thread(target=start).start()
    except KeyboardInterrupt:
        pocket.store.dispatch(Terminate(reset_flag=False))
        reducer_loop(pocket)  # need to start reducer loop again to handle the terminate action just dispatcher


def start():
    logger.info('Starting...')
    pocket = Pocket()
    init_scripts(pocket)
    reducer_loop(pocket)
