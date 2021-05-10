import logging
from functools import partial
from typing import Optional, Callable
from urllib import request
from pathlib import Path
import os

from telegram.ext import CommandHandler

from src.utils.affiliates import BaseAction
from src.core.actions import TelegramBotInitiated, AddServerHandler
from src.core.start import Pocket
import telegram_handler
import http_handler

try:
    import pdf2image
    pdf2image_error = False
except ImportError as e:
    pdf2image_error = True


logger = logging.getLogger(__name__)


def init(pocket: Pocket):
    if pdf2image_error:
        logger.info('Cannot import pdf2image. Try: pip install pdf2image')

    helper = PDFHelper(output_dir_name='output')
    pocket.set(__name__, helper)
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/page/', http_handler.get_pdf_html_page))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/image/', http_handler.get_pdf_image))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/raw/', http_handler.get_raw_pdf))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/counts/', http_handler.get_database_status))


def init_bot_handlers(action: BaseAction, pocket: Pocket):
    dispatcher = pocket.telegram_updater.dispatcher
    dispatcher.add_handler(CommandHandler("pdf", telegram_handler.pdf_request))
    dispatcher.add_handler(CommandHandler("pdfsync", telegram_handler.sync_database_telegram))


class PDFHelper:
    def __init__(self, output_dir_name):
        self.output_dir_path = Path(__file__).parent / output_dir_name
        self.output_pdf_name = 'output.pdf'
        self.output_image_name = '%d.jpg'
        self.pdf_len_cache = {}  # cache lengths instead of scanning os each time

        # Create output directory if not exists
        self.output_dir_path.mkdir(exist_ok=True)

    def _get_next_id(self):
        dir_names = sorted(next(os.walk(self.output_dir_path))[1])
        next_valid_id = 1
        for name in dir_names:
            if name == str(next_valid_id):
                next_valid_id += 1
        return str(next_valid_id)

    def download(self, url: str, reporthook: Callable[[int, int, int], None] = None) -> str:
        next_id = self._get_next_id()
        pdf_path = self.get_pdf_path(next_id, make_dir=True)
        request.urlretrieve(url, filename=pdf_path, reporthook=reporthook)
        return next_id

    def generate_images(self, dir_id: str, dpi=200):
        if convert_from_path is None:
            return None
        return convert_from_path(self.get_pdf_path(dir_id), dpi)

    def save_images_to_files(self, dir_id: str, pages) -> None:
        for i, page in enumerate(pages):
            page.save(self.get_page_path(dir_id, i), 'JPEG')

    def get_number_of_pages(self, dir_id: int) -> Optional[int]:
        if dir_id not in self.pdf_len_cache:
            self.pdf_len_cache[dir_id] = len(os.listdir(self.output_dir_path / dir_id)) - 1
        return self.pdf_len_cache[dir_id]

    def get_page_path(self, dir_id: str, page_num: int):
        return self.output_dir_path / dir_id / (self.output_image_name % page_num)

    def get_pdf_path(self, dir_id: str, make_dir=False):
        if make_dir:
            (self.output_dir_path / dir_id).mkdir()
        return self.output_dir_path / dir_id / self.output_pdf_name

