import os
from configparser import ConfigParser
from pathlib import Path
import importlib
import logging

logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    return Path(__file__).parent.parent.parent


def get_handlers_path_relative() -> Path:
    """Returns the path of the handlers directory relative to the main directory. Needed to dynamically import"""
    return get_project_root() / 'src' / 'handlers'


def get_handlers_import_path_relative() -> str:
    """Returns the import path of the handlers directory relative to the main directory. Needed to dynamically import"""
    return 'src.handlers'


def get_db_path() -> Path:
    """Returns a path to the project database directory, and init the directory not exists"""
    result = get_project_root() / 'database' / 'active'
    result.mkdir(exist_ok=True, parents=True)
    return result


def init_config(config_path=None) -> ConfigParser:
    try:
        config = ConfigParser()
        if config_path is None:
            config.read('settings.ini')
        else:
            config.read(config_path)

        if len(config.sections()) == 0:
            raise FileNotFoundError('No file found / no sections found in settings.ini file: (%s)' % config_path)

        return config
    except Exception:
        logger.exception('Failed to load settings .ini file: (%s). Terminating' % config_path)
        raise


def get_all_scripts(function_name_check: str, script_module_import_path: str = None,
                    script_module_path: Path = None, recursive: bool = False):
    if script_module_import_path is None:
        script_module_import_path = get_handlers_import_path_relative()
    if script_module_path is None:
        script_module_path = get_handlers_path_relative()

    importlib.invalidate_caches()
    script_names = [f[:-3] for f in os.listdir(script_module_path) if f.endswith('.py')]
    module_list = []

    for sn in script_names:
        try:
            module = importlib.import_module('.' + sn, script_module_import_path)
            module = importlib.reload(module)
            if hasattr(module, function_name_check) and callable(getattr(module, function_name_check)):
                module_list.append(module)
            else:
                # logger.warning('Dynamically imported script "' + sn + '.py" has no callable ' + function_name_check)
                pass
        except Exception as e:
            logger.error('Error occurred while dynamically importing script "' + sn + '.py"', exc_info=e)

    # collect inner directories to repeat recursively
    if recursive:
        inner_directories = [f for f in os.listdir(script_module_path) if os.path.isdir(script_module_path / f)]
        for inner_dir_name in inner_directories:
            inner_import_path = script_module_import_path + '.' + inner_dir_name
            inner_path = script_module_path / inner_dir_name
            module_list += get_all_scripts(function_name_check, inner_import_path, inner_path, recursive=True)

    return module_list
