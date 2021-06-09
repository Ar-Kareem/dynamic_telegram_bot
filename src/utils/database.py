import os
from pathlib import Path
from shutil import rmtree
from configparser import ConfigParser
import pickle
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # suggested by stackoverflow.com/questions/36117046/


_METADATA_FILENAME = '.metadata.ini'


def compress(dir_path, output_file, encrypt_key, metadata_key=None):
    result = {'name': dir_path.name, 'folders': []}
    dirs = [dir_path / n for n in os.listdir(dir_path) if (dir_path / n).is_dir()]
    for d in dirs:
        if metadata_key is not None:
            config = ConfigParser()
            config.read(d / _METADATA_FILENAME)
            key = config.getboolean('METADATA', metadata_key, fallback=False)
            if not key:  # does not pass the check
                continue
        result['folders'].append(_collect_dir(d))

    # pickle dictionary, use protocol 4 which was added in python 3.4 (5 only added in 3.8 so not using it)
    result_bytes = pickle.dumps(result, protocol=4)
    # encrypt bytes
    nonce = secrets.token_bytes(12)  # GCM mode needs 12 fresh bytes every time
    result_bytes = nonce + AESGCM(encrypt_key).encrypt(nonce, result_bytes, b"")
    with open(output_file, 'wb') as f:
        f.write(result_bytes)


def _collect_dir(dir_path: Path):
    """ Recursive function to crawl into all files inside a folder and collect all data """
    result = {'name': dir_path.name, 'folders': [], 'files': []}
    for f in os.listdir(dir_path):
        f = dir_path / f
        if f.is_dir():  # folder recursive case
            result['folders'].append(_collect_dir(f))
        else:  # file
            file_data = {'name': f.name, 'data': bytes()}
            with open(f, 'rb') as open_file:
                file_data['data'] = open_file.read()
            result['files'].append(file_data)
    return result


def decompress(db_file, output_dir, decrypt_key, hard_overwrite=False):
    with open(db_file, 'rb') as f:
        db_bytes = f.read()
    # decrypt
    db_bytes = AESGCM(decrypt_key).decrypt(db_bytes[:12], db_bytes[12:], b"")
    db_dict = pickle.loads(db_bytes)

    # create the output directory
    db_dir = (output_dir / db_dict['name'])
    db_dir.mkdir(exist_ok=True)
    for folder_data in db_dict['folders']:
        _expand_collected_dir(folder_data, cur_path=db_dir, hard_overwrite=hard_overwrite)


def _expand_collected_dir(data: dict, cur_path: Path, hard_overwrite: bool):
    cur_folder = cur_path / data['name']
    if cur_folder.exists():  # folder already exists, either overwrite it or exit
        if hard_overwrite:
            rmtree(cur_folder)
        else:
            print('cannot expand already existing folder unless hard_overwrite is on')
            return
    cur_folder.mkdir()
    for sub_folder in data['folders']:
        _expand_collected_dir(sub_folder, cur_path=cur_folder, hard_overwrite=hard_overwrite)
    for file_data in data['files']:
        file_path = cur_folder / file_data['name']
        if file_path.exists():
            # print('file already exists...', file_path)
            continue
        with open(file_path, 'wb') as f:
            f.write(file_data['data'])


def _print_random_key(length=32):
    k = secrets.token_bytes(length)
    print("".join('\\x%02x' % b for b in k))


def string_to_key(_key):
    return b''.join([int(_key[i+2:i+4], 16).to_bytes(1, 'little') for i in range(0, len(_key), 4)])