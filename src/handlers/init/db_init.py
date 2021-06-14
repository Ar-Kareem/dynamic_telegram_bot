import os
from pathlib import Path
import logging

from src.core.start import Pocket
from src.utils.database import decompress, date_delete_callback, string_to_key

logger = logging.getLogger(__name__)


def init(pocket: Pocket):
    _key = pocket.config.get('DATABASE', 'key', fallback=None)
    if _key is None:
        logger.error('DB key not found in config')
        return
    _key = string_to_key(_key)

    db_root = pocket.database_dir.parent
    encrypted = Path(db_root / 'encrypted')

    db_files = [encrypted / db_file for db_file in os.listdir(encrypted)]
    for db_file in db_files:
        decompress(db_file=db_file, output_dir=db_root, decrypt_key=_key, rm_callback=date_delete_callback)
