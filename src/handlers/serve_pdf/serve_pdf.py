import logging
from functools import partial
from typing import Optional, Callable
from urllib import request
from pathlib import Path
import os
import json

from telegram import Update, MessageEntity
from telegram.ext import CommandHandler, CallbackContext

from src.utils.affiliates import BaseAction
from src.utils.simple_server.simple_server import MyHTTPHandler

try:
    import pdf2image
    from pdf2image import convert_from_path
except ImportError as e:
    convert_from_path = None

from src.core.actions import TelegramBotInitiated, AddServerHandler
from src.core.start import Pocket


logger = logging.getLogger(__name__)


def init(pocket: Pocket):
    if convert_from_path is None:
        logger.info('Cannot import pdf2image. Try: pip install pdf2image')

    helper = _Helper(output_dir_name='output')
    pocket.set(__name__, helper)
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/page/', get_pdf_html_page))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/image/', get_pdf_image))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/raw/', get_raw_pdf))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/counts/', get_database_status))


def init_bot_handlers(action: BaseAction, pocket: Pocket):
    dispatcher = pocket.telegram_updater.dispatcher
    dispatcher.add_handler(CommandHandler("pdf", pdf_request))
    dispatcher.add_handler(CommandHandler("pdfsync", sync_database_telegram))


class _Helper:
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


def pdf_request(update: Update, context: CallbackContext) -> None:
    # https://arxiv.org/pdf/1905.11397.pdf
    pocket: Pocket = context.bot_data['pocket']
    helper: _Helper = pocket.get(__name__)
    for entity in update.effective_message.entities:
        if entity.type == MessageEntity.URL:
            a, b = entity.offset, entity.offset+entity.length
            url = update.effective_message.text[a:b]
            url = url if url.startswith('http') else 'http://' + url
            break
    else:
        update.effective_message.reply_text('no url found')
        return
    try:
        msg = '1/4 - url found: %s. Downloading...' % url
        message_to_user = update.effective_message.reply_text(msg)

        import math
        import time

        def reporthook(a, b, c, last_telegram_update_time=[0.0], last_telegram_update_percent=[-1]):
            percent_done = int(50*a / math.ceil((c if c > 0 else 1) / (b if b > 0 else 1)))
            percent_left = 50-percent_done
            if last_telegram_update_time[-1] + 0.5 < time.time() and last_telegram_update_percent[-1] != percent_done:
                last_telegram_update_time.append(time.time())
                last_telegram_update_percent.append(percent_done)
                message_to_user.edit_text(msg +
                                          '\n' + (percent_done*'+') + (percent_left*'~') + f' ({2*percent_done} %)')

        pdf_id = helper.download(url, reporthook=reporthook)
        message_to_user.edit_text('2/4 - Downloaded. Converting to images...')
        images = helper.generate_images(pdf_id)
        message_to_user.edit_text('3/4 - Converted. Number of pages: %d. Saving to disk...' % len(images))
        helper.save_images_to_files(pdf_id, images)
        website_url = pocket.config.get('SERVER', 'url', fallback='')
        message_to_user.edit_text(f'Done (id: {pdf_id}). Link: {website_url}/pdf/page/{pdf_id}/0')
    except Exception:
        logger.exception('Error while serving PDF.')
        update.effective_message.reply_text('Error occurred. Check logs.')


def get_pdf_html_page(self: MyHTTPHandler):
    try:
        pdf_id = int(self.path.split('/')[3])
        pdf_id = str(pdf_id)
        page_num = int(self.path.split('/')[4])
    except Exception as ex:
        logger.error(ex)
        self.send_response(403)
        self.end_headers()
        return
    helper: _Helper = self.pocket.get(__name__)
    page_path = helper.get_page_path(pdf_id, page_num)
    if page_path is None:
        self.send_response(403)
        self.end_headers()
        return

    # prepare html
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()

    prev_page_button = f'<a href="/pdf/page/{pdf_id}/{page_num-1}" class="button green">Prev</a>' if page_num > 0 else ''
    next_page_button = f'<a href="/pdf/page/{pdf_id}/{page_num+1}" class="button blue">Next</a>' \
        if page_num < helper.get_number_of_pages(pdf_id)-1 else ''

    img = f'<img src="/pdf/image/{pdf_id}/{page_num}" >'  # style="width:50px;height:50px;"
    html = ''' 
    <html>
    <head>
    <style>
    .blue {background-color: #4CAF50;} /* Green */
    .green {background-color: #008CBA;} /* Blue */
    a.button {
        -webkit-appearance: button;
        -moz-appearance: button;
        appearance: button;
    
        text-decoration: none;
        border: none;
        color: white;
        padding: 15px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 120px;
        margin: 4px 70px;
        cursor: pointer;
    }
    </style>
    </head>
    '''
    html += f'''
    <body>
        {img}
        {prev_page_button}
        {next_page_button}
    </body>
    </html>
    '''
    self.wfile.write(bytes(html, "utf-8"))


def get_pdf_image(self: MyHTTPHandler):
    try:
        pdf_id = int(self.path.split('/')[3])
        pdf_id = str(pdf_id)
        page_num = int(self.path.split('/')[4])
    except Exception:
        self.send_response(403)
        self.end_headers()
        return
    helper: _Helper = self.pocket.get(__name__)
    page_path = helper.get_page_path(pdf_id, page_num)
    if page_path is None:
        self.send_response(403)
        self.end_headers()
        return
    self.send_response(200)
    self.send_header('Content-type', 'image/jpg')
    self.end_headers()
    with open(page_path, 'rb') as f:
        self.wfile.write(f.read())


def get_raw_pdf(self: MyHTTPHandler):
    try:
        pdf_id = int(self.path.split('/')[3])
        pdf_id = str(pdf_id)
    except Exception:
        self.send_response(403)
        self.end_headers()
        return
    helper: _Helper = self.pocket.get(__name__)
    pdf_path = helper.get_pdf_path(pdf_id)
    if pdf_path is None:
        self.send_response(403)
        self.end_headers()
        return
    self.send_response(200)
    self.send_header('Content-type', 'application/pdf')
    self.end_headers()
    with open(pdf_path, 'rb') as f:
        self.wfile.write(f.read())


def get_database_status(self: MyHTTPHandler):
    path = [subpath for subpath in self.path.split('/')[3:] if subpath != '']
    helper: _Helper = self.pocket.get(__name__)
    if len(path) == 0:
        resp = os.listdir(helper.output_dir_path)
    elif len(path) == 1:
        pdf_id = str(int(path[0]))
        pages = helper.get_number_of_pages(pdf_id)
        size = os.path.getsize(helper.get_pdf_path(pdf_id))
        resp = {'pages': pages, 'size': size}
    else:
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        return
    self.send_response(200)
    self.send_header('Content-type', 'application/json')
    self.end_headers()
    self.wfile.write(json.dumps(resp).encode('utf-8'))


def sync_database_telegram(update: Update, context: CallbackContext) -> None:
    # https://arxiv.org/pdf/1905.11397.pdf
    pocket: Pocket = context.bot_data['pocket']
    helper: _Helper = pocket.get(__name__)
    for entity in update.effective_message.entities:
        if entity.type == MessageEntity.URL:
            a, b = entity.offset, entity.offset+entity.length
            url = update.effective_message.text[a:b]
            url = url if url.startswith('http') else 'http://' + url
            break
    else:
        update.effective_message.reply_text('no url found')
        return
    try:
        unimportant_msg = None
        def report_hook(msg: str, important: bool = False):
            nonlocal unimportant_msg
            if unimportant_msg is None:
                unimportant_msg = update.effective_message.reply_text(msg)
            else:
                unimportant_msg.edit_text(msg)
            unimportant_msg = unimportant_msg if not important else None

        sync_database(url, report_hook)
    except Exception:
        logger.exception('Error while syncing database.')
        update.effective_message.reply_text('Error occurred. Check logs.')


def sync_database(url, report_hook):
    target_dir = Path(__file__).parent / 'output'
    url_counts = url + '/pdf/counts'
    url_raw = url + '/pdf/raw'
    url_image = url + '/pdf/image'
    output_pdf_name = 'output.pdf'

    def url_get(url: str):
        with request.urlopen(url) as r:
            return json.loads(r.read())

    target_dir.mkdir(exist_ok=True)
    target_dir_files = os.listdir(target_dir)
    report_hook(f'Getting source PDF count from {url_counts}...', False)
    pdfs = url_get(url_counts)
    report_hook(f'Total pdf {len(pdfs)}', True)
    for pdf_id in pdfs:
        cur_stats = url_get(url_counts + '/' + pdf_id)
        cur_dir = target_dir / pdf_id
        if not Path(cur_dir).exists() or len(os.listdir(cur_dir)) == 0:  # folder doesn't exists or empty
            Path(cur_dir).mkdir(exist_ok=True)
            # start syncing (download pdf and images)
            report_hook(f'{pdf_id} Downloading PDF...', False)
            request.urlretrieve(url_raw + '/' + pdf_id, cur_dir / output_pdf_name)
            for i in range(cur_stats['pages']):
                report_hook(f'{pdf_id} Downloading page {i}...', False)
                request.urlretrieve(url_image + '/' + pdf_id + '/' + str(i), cur_dir / (str(i) + '.jpg'))
        else:  # folder already exists and has content
            # need to check that folder content matches server otherwise desync
            cur_dir_files = os.listdir(cur_dir)
            jpg_count = len([f for f in cur_dir_files if f.endswith('.jpg')])
            if output_pdf_name not in cur_dir_files:
                report_hook(f'{pdf_id} DESYNC pdf doesnt exist', True)
            elif os.path.getsize(cur_dir / output_pdf_name) != cur_stats['size']:
                report_hook(f'{pdf_id} DESYNC in pdf size', True)
            elif len(cur_dir_files) - 1 != cur_stats['pages']:
                report_hook(f'{pdf_id} DESYNC in pages', True)
            else:
                report_hook(f'{pdf_id} Good.', False)
    report_hook(f'Done.', True)
