import logging
from functools import partial

from telegram.ext import CommandHandler

from src.utils.affiliates import BaseAction
from src.core.actions import TelegramBotInitiated, AddServerHandler
from src.core.pocket import Pocket
import src.handlers.serve_pdf.telegram_handler as telegram_handler
import src.handlers.serve_pdf.http_handler as http_handler
from src.handlers.serve_pdf.helper import PDFHelper, DICT_NAME

try:
    import pdf2image
    pdf2image_error = False
except ImportError as e:
    pdf2image_error = True


logger = logging.getLogger(__name__)


def init(pocket: Pocket):
    if pdf2image_error:
        logger.info('Cannot import pdf2image. Try: pip install pdf2image.')
        logger.info('On linux some linux distros (PI), you might have to apt-get libopenjp2-7 libtiff5')

    helper = PDFHelper(output_dir=(pocket.database_dir / 'serve_pdf_output'))
    pocket.set(DICT_NAME, helper)
    pocket.reducer.register_handler(trigger=TelegramBotInitiated, callback=partial(init_bot_handlers, pocket=pocket))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/page/', http_handler.get_pdf_html_page))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/image/', http_handler.get_pdf_image))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/raw/', http_handler.get_raw_pdf))
    pocket.store.dispatch(AddServerHandler('get', '/pdf/counts/', http_handler.get_database_status))


def init_bot_handlers(action: BaseAction, pocket: Pocket):
    dispatcher = pocket.telegram_updater.dispatcher
    dispatcher.add_handler(CommandHandler("pdf", telegram_handler.pdf_request))
    dispatcher.add_handler(CommandHandler("pdfsync", telegram_handler.sync_database_telegram))

