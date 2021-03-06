import logging
import os
from pathlib import Path
from shutil import rmtree
from configparser import ConfigParser
from datetime import datetime
import pickle
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # suggested by stackoverflow.com/questions/36117046/
from typing import List, NamedTuple

logger = logging.getLogger(__name__)
_METADATA_FILENAME = '.metadata.ini'

FileRecord = NamedTuple('FileRecord', [('name', str), ('data', bytes)])
DirectoryRecord = NamedTuple('DirectoryRecord', [('name', str),
                                                 ('folders', List['DirectoryRecord']), ('files', List[FileRecord])])
RootRecord = NamedTuple('RootRecord', [('name', str), ('folders', List[DirectoryRecord]), ('date', str)])


def compress(dir_path: Path, output_file: str, encrypt_key: bytes, check_callback=None, verbose=False):

    result = RootRecord(name=dir_path.name, folders=[], date=datetime.today().strftime('%Y-%m-%d-%H:%M:%S'))

    dirs: List[Path] = [dir_path / n for n in os.listdir(dir_path) if (dir_path / n).is_dir()]
    for d in dirs:
        if check_callback is not None:
            config = ConfigParser()
            config.read(d / _METADATA_FILENAME)
            if not check_callback(d, config):  # callback returned false, do not compress
                continue
        directory_record = _collect_dir(d)
        result.folders.append(directory_record)
        if verbose:
            logger.info('dir: %s. files %s', d.name, ','.join([n.name for n in directory_record.files]))
    # pickle dictionary, use protocol 4 which was added in python 3.4 (5 only added in 3.8 so not using it)
    result_bytes = pickle.dumps(result, protocol=4)
    # encrypt bytes
    nonce = secrets.token_bytes(12)  # GCM mode needs 12 fresh bytes every time
    result_bytes = nonce + AESGCM(encrypt_key).encrypt(nonce, result_bytes, b"")
    with open(output_file, 'wb') as f:
        f.write(result_bytes)


def _collect_dir(dir_path: Path) -> DirectoryRecord:
    """ Recursive function to crawl into all files inside a folder and collect all data """
    result = DirectoryRecord(name=dir_path.name, folders=[], files=[])

    for f in os.listdir(dir_path):
        f = dir_path / f
        if f.is_dir():  # folder recursive case
            result.folders.append(_collect_dir(f))
        else:  # file
            with open(f, 'rb') as open_file:
                file_bytes = open_file.read()
            file_record = FileRecord(name=f.name, data=file_bytes)
            result.files.append(file_record)
    return result


def decompress(db_file: str, output_dir: Path, decrypt_key: bytes, rm_callback=None, verbose=False):
    with open(db_file, 'rb') as f:
        db_bytes = f.read()
    # decrypt
    try:
        db_bytes = AESGCM(decrypt_key).decrypt(db_bytes[:12], db_bytes[12:], b"")
        root_record: RootRecord = pickle.loads(db_bytes)
    except Exception as e:
        logger.exception('Failed to decrypt DB. %s, %e', db_file, e)
        return

    # create the output directory
    db_dir = (output_dir / root_record.name)
    db_dir.mkdir(parents=True, exist_ok=True)
    if verbose:
        logger.info('Unpacking in directory: %s', db_dir)

    compression_date_str = root_record.date
    compression_date = datetime.strptime(compression_date_str, '%Y-%m-%d-%H:%M:%S')

    for folder_data in root_record.folders:
        cur_folder = db_dir / folder_data.name
        config = ConfigParser()
        config.read(cur_folder / _METADATA_FILENAME)
        if cur_folder.exists():
            # folder already exists, ask the callback function what to do, giving it folder path and compression date
            if rm_callback is not None and rm_callback(cur_folder, config, compression_date):
                if verbose:
                    logger.info('Deleting dir %s as rm_callback returned False', cur_folder)
                rmtree(cur_folder)
            else:
                if verbose:
                    logger.info('skipping unpacking %s as rm_callback returned False', cur_folder)
                continue
        if verbose:
            logger.info('unpacking dir: %s, files %s', folder_data.name, ','.join([n.name for n in folder_data.files]))

        _expand_collected_dir(folder_data, cur_path=db_dir)
        # add the decompression date to the metadata
        if not config.has_section('METADATA'):
            config.add_section('METADATA')
        config.set('METADATA', 'restored_from', compression_date_str)
        with open(cur_folder / _METADATA_FILENAME, 'w') as configfile:
            config.write(configfile)


def _expand_collected_dir(directory_records: DirectoryRecord, cur_path: Path):
    cur_folder = cur_path / directory_records.name
    cur_folder.mkdir()
    for sub_folder in directory_records.folders:
        _expand_collected_dir(sub_folder, cur_path=cur_folder)
    for file_data in directory_records.files:
        file_path = cur_folder / file_data.name
        if file_path.exists():
            logger.info('file already exists... (%s)', file_path)
            continue
        with open(file_path, 'wb') as f:
            f.write(file_data.data)


def _print_random_key(length=32):
    k = secrets.token_bytes(length)
    logger.info("".join('\\x%02x' % b for b in k))


def string_to_key(_key):
    return b''.join([int(_key[i+2:i+4], 16).to_bytes(1, 'little') for i in range(0, len(_key), 4)])


def date_delete_callback(fldr_path: Path, fldr_config: ConfigParser, db_date: datetime):
    """Helper function implementing a delete callback that compares dates
    It will compare the date from the encrypted db file with the date of the decompressed directory config file
    if the encrypted db is newer than the decompressed directory then it will decide to overwrite the old directory
    """
    parsed = fldr_config.get('METADATA', 'restored_from', fallback=None)
    if parsed is None:
        logger.info('cannot determine if db copy is newer or older since .ini file does not contain date')
        return False
    fldr_date = datetime.strptime(parsed, '%Y-%m-%d-%H:%M:%S')
    # logger.info(db_date > fldr_date, fldr_path.name, fldr_date, db_date)
    return db_date > fldr_date
