import os
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


def get_all_scripts(function_name_check: str, script_module_import_path: str = None, script_module_path: Path = None):
    if script_module_import_path is None:
        script_module_import_path = get_handlers_import_path_relative()
    if script_module_path is None:
        script_module_path = get_handlers_path_relative()

    importlib.invalidate_caches()
    print(os.listdir(script_module_path))
    script_names = [f.rstrip('.py') for f in os.listdir(script_module_path) if f.endswith('.py')]
    module_list = []

    for sn in script_names:
        try:
            module = importlib.import_module('.' + sn, script_module_import_path)
            module = importlib.reload(module)
            if hasattr(module, function_name_check) and callable(getattr(module, function_name_check)):
                module_list.append(module)
            else:
                logger.warning('Dynamically imported script "' + sn + '.py" has no callable ' + function_name_check)
        except Exception as e:
            logger.error('Error occurred while dynamically importing script "' + sn + '.py"', exc_info=e)
    return module_list
