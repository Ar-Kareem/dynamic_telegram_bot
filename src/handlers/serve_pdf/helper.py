import logging
from typing import Optional, Callable
from urllib import request
from pathlib import Path
import os


try:
    import pdf2image
    from pdf2image import convert_from_path
    pdf2image_error = False
except ImportError as e:
    convert_from_path = None
    pdf2image_error = True


logger = logging.getLogger(__name__)
DICT_NAME = 'serve_pdf'


class PDFHelper:
    def __init__(self, output_dir):
        self.output_dir_path = output_dir
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

