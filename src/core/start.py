import sys
from pathlib import Path
from threading import Thread
import logging

from src.core.actions import InitScriptsFinished, Terminate
from src.utils import utils
from src.core.pocket import Pocket

logger = logging.getLogger(__name__)


def start(config_path=None):
    init_logger()
    pocket = Pocket(config_path=config_path)
    init_scripts(pocket)
    reducer_loop(pocket, config_path)


def init_logger():
    Path("logs").mkdir(exist_ok=True)
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


def init_scripts(pocket: Pocket):
    scripts = utils.get_all_scripts(function_name_check='init', recursive=True)
    for script in scripts:
        # noinspection PyBroadException
        try:
            script.init(pocket)
        except Exception:
            logger.exception('Exception in dynamic init for script ' + script.__name__ + '.py"')
    pocket.store.dispatch(InitScriptsFinished())


def reducer_loop(pocket: Pocket, *restart_args):
    try:
        last_action: Terminate = pocket.reducer.start(stop_action=Terminate)
        if last_action.reset_flag:
            Thread(target=start, args=restart_args).start()
    except KeyboardInterrupt:
        pocket.store.dispatch(Terminate())
        pocket.reducer.start(stop_action=Terminate)  # need handle the terminate action just dispatched
