import logging
from functools import partial
from typing import Optional, Callable
from urllib import request
from pathlib import Path

from telegram import Update, MessageEntity
from telegram.ext import CommandHandler, CallbackContext

from src.utils.affiliates import BaseAction
from src.utils.simple_server.simple_server import MyHTTPHandler

try:
    import pdf2image
    from pdf2image import convert_from_path
except ImportError as e:
    pass

from src.core.actions import TelegramBotInitiated, AddServerHandler
from src.core.start import Pocket


logger = logging.getLogger(__name__)


class _Helper:
    def __init__(self, output_dir_name):
        self.output_dir_name = output_dir_name
        self.output_dir_path = Path(__file__).parent / self.output_dir_name
        self.output_pdf_path = self.output_dir_path / 'output.pdf'
        self.output_image_name = 'out_%d.jpg'
        # Create output directory
        self.output_dir_path.mkdir(exist_ok=True)

        self.pages = []
        self.converted_to_files = False

    def download(self, url: str, reporthook: Callable[[int, int, int], None] = None) -> None:
        request.urlretrieve(url, filename=self.output_pdf_path, reporthook=reporthook)
        self.pages = None
        self.converted_to_files = False

    def generate_images(self, dpi=200) -> None:
        self.pages = convert_from_path(self.output_pdf_path, dpi)

    def save_images_to_files(self) -> None:
        if self.pages is None:
            return
        for i, page in enumerate(self.pages):
            current_out_name = self.output_image_name % i
            page.save(self.output_dir_path / current_out_name, 'JPEG')
        self.converted_to_files = True

    def get_number_of_pages(self) -> Optional[int]:
        if self.pages is None:
            return None
        return len(self.pages)

    def get_page_path(self, page_num):
        if self.pages is None or not self.converted_to_files:
            return
        if 0 <= page_num < len(self.pages):
            return self.output_dir_path / (self.output_image_name % page_num)
        return


def telegram(update: Update, context: CallbackContext) -> None:
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
            percent_done = int(50*a / math.ceil(c / b))
            percent_left = 50-percent_done
            if last_telegram_update_time[-1] + 0.5 < time.time() and last_telegram_update_percent[-1] != percent_done:
                last_telegram_update_time.append(time.time())
                last_telegram_update_percent.append(percent_done)
                message_to_user.edit_text(msg +
                                          '\n' + (percent_done*'+') + (percent_left*'~') + f' ({2*percent_done} %)')

        helper.download(url, reporthook=reporthook)
        message_to_user.edit_text('2/4 - Downloaded. Converting to images...')
        helper.generate_images()
        message_to_user.edit_text('3/4 - Converted. Number of pages: %d. Saving to disk...'
                                  % helper.get_number_of_pages())
        helper.save_images_to_files()
        website_url = pocket.config.get('SERVER', 'url', fallback='')
        message_to_user.edit_text(f'Done. Link: {website_url}/pdf/page/0')
    except Exception:
        logger.exception('Error while serving PDF.')
        update.effective_message.reply_text('Error occured. Check logs.')


def init_bot_handlers(action: BaseAction, pocket: Pocket):
    dispatcher = pocket.telegram_updater.dispatcher
    dispatcher.add_handler(CommandHandler("pdf", telegram))


def init(pocket: Pocket):
    try:
        import pdf2image
    except ImportError:
        logger.info('Cannot import pdf2image. Skipping %s. Try: pip install pdf2image', __name__)
        return

    helper = _Helper(output_dir_name='output')
    pocket.set(__name__, helper)
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/page/', get_pdf_page))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/image/', get_pdf_image))


def get_pdf_page(self: MyHTTPHandler):
    try:
        digit = int(self.path.split('/')[3])
    except Exception:
        self.send_response(403)
        self.end_headers()
        return
    helper: _Helper = self.pocket.get(__name__)
    page_path = helper.get_page_path(digit)
    if page_path is None:
        self.send_response(403)
        self.end_headers()
        return

    # prepare html
    self.send_response(200)
    self.send_header("Content-type", "text/html")
    self.end_headers()

    prev_page_button = f'<a href="/pdf/page/{digit-1}" class="button green">Prev</a>' if digit > 0 else ''
    next_page_button = f'<a href="/pdf/page/{digit+1}" class="button blue">Next</a>' \
        if digit < helper.get_number_of_pages()-1 else ''

    img = f'<img src="/pdf/image/{digit}" >'  # style="width:50px;height:50px;"
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
        digit = int(self.path.split('/')[3])
    except Exception:
        self.send_response(403)
        self.end_headers()
        return
    helper: _Helper = self.pocket.get(__name__)
    page_path = helper.get_page_path(digit)
    if page_path is None:
        self.send_response(403)
        self.end_headers()
        return
    self.send_response(200)
    self.send_header('Content-type', 'image/jpg')
    self.end_headers()
    with open(page_path, 'rb') as f:
        self.wfile.write(f.read())

