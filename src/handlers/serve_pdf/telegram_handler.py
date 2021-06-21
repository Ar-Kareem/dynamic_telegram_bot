import logging
from urllib import request
from pathlib import Path
import os
import json
import math
import time

from telegram import Update, MessageEntity
from telegram.ext import CallbackContext

from src.core.pocket import Pocket
from src.handlers.serve_pdf.helper import PDFHelper, DICT_NAME

try:
    import pdf2image
    from pdf2image import convert_from_path
except ImportError as e:
    convert_from_path = None


logger = logging.getLogger(__name__)


def pdf_request(update: Update, context: CallbackContext) -> None:
    # https://arxiv.org/pdf/1905.11397.pdf
    pocket: Pocket = context.bot_data['pocket']
    helper: PDFHelper = pocket.get(DICT_NAME)
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


def sync_database_telegram(update: Update, context: CallbackContext) -> None:
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
        prev_msg = None

        def report_hook(msg: str, important: bool = False):
            nonlocal prev_msg
            if prev_msg is None:
                prev_msg = update.effective_message.reply_text(msg)
            else:
                prev_msg.edit_text(msg)
            prev_msg = prev_msg if not important else None

        pocket: Pocket = context.bot_data['pocket']
        target_dir = pocket.database_dir / 'serve_pdf_output'
        _sync_database(url, target_dir, report_hook)
    except Exception:
        logger.exception('Error while syncing database.')
        update.effective_message.reply_text('Error occurred. Check logs.')


def _sync_database(url, target_dir, report_hook):
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
