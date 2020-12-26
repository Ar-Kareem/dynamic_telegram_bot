import os
import sys
import time
import importlib
import logging
import configparser

from telegram.ext import Updater

warn_file_handler = logging.FileHandler(filename='logs_warn.log')
warn_file_handler.setLevel(logging.WARN)
debug_file_handler = logging.FileHandler(filename='logs_debug.log')
debug_file_handler.setLevel(logging.DEBUG)
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.DEBUG)
handlers = [stderr_handler, debug_file_handler, warn_file_handler]

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(filename)s:%(lineno)d - %(name)s} %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

try:
    config = configparser.ConfigParser()
    config.read('settings.ini')
except Exception:
    logger.exception('Failed to load settings.ini file. Terminating')
    raise


def get_config(section, key):
    return config[section][key]


def send_myself_message(message, updater):
    updater.bot.send_message(chat_id=updater.dispatcher.bot_data['global_flags']['my_chat_id'], text=message)


def init_new_bot():
    """To initialize a new bot, will reset global flags and return the updater"""
    logger.info('Initializing New Bot...')
    botkey = get_config('TOKENS', 'telegram')
    updater = Updater(botkey, use_context=True)
    updater.dispatcher.bot_data['global_flags'] = get_init_global_flags()
    return updater


def get_init_global_flags():
    initial_state = {'reset_flag': False,
                     'terminate_flag': False,
                     'starttime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                     'my_chat_id': 134936683,
                     }
    return initial_state


def init_dispatcher(updater):
    script_modules = get_all_handler_scripts(parent_folder_path='handlers', function_name_check='init_handlers')
    for script in script_modules:
        try:
            script.init_handlers(updater)
        except Exception as e:
            logger.error('Error occurred while calling init_handlers for scripts ' + script.__name__ + '.py"',
                         exc_info=e)
    # Send me a message
    logger.info('Bot Started, sending message to me.')
    send_myself_message('STARTED', updater)


def get_all_handler_scripts(parent_folder_path='handlers', function_name_check='init_handlers'):
    importlib.invalidate_caches()
    script_names = [f.rstrip('.py') for f in os.listdir(parent_folder_path) if f.endswith('.py')]
    module_list = []

    for sn in script_names:
        try:
            module = importlib.import_module('.' + sn, parent_folder_path)
            module = importlib.reload(module)
            if hasattr(module, function_name_check) and callable(getattr(module, function_name_check)):
                module_list.append(module)
            else:
                logger.warning('script "' + sn + '.py" has no callable ' + function_name_check)
        except Exception as e:
            logger.error('Error occurred while importing handler script "' + sn + '.py"', exc_info=e)
    return module_list


def wait_until_terminate_flag(global_flags, period=2.5):
    while not global_flags['terminate_flag']:
        print('tic', time.sleep)
        time.sleep(period)
        print('toc', time.sleep)


def main_bot_loop():
    while True:
        updater = init_new_bot()
        global_flags = updater.dispatcher.bot_data['global_flags']
        try:
            init_dispatcher(updater)
            updater.start_polling()
            wait_until_terminate_flag(global_flags)
        except KeyboardInterrupt:
            logger.info('Keyboard Interrupt')
            global_flags['terminate_flag'] = True  # in an attempt to gracefully kill all threads that monitor this
            sys.exit()
        finally:
            logger.info('Stopping Bot!')
            updater.stop()
            del updater

        if global_flags['reset_flag']:
            logger.info('Resetting Bot')
        else:
            logger.info('Exiting Script')
            break


def main():
    main_bot_loop()


if __name__ == '__main__':
    main()
