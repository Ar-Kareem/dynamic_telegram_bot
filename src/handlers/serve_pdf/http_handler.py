import logging
import os
import json
from http import HTTPStatus

from src.handlers.serve_pdf.helper import PDFHelper, DICT_NAME

from src.utils.simple_server.simple_server import MyHTTPHandler, InternalServerError

logger = logging.getLogger(__name__)


def get_pdf_html_page(self: MyHTTPHandler):
    try:
        pdf_id = int(self.path.split('/')[3])
        pdf_id = str(pdf_id)
        page_num = int(self.path.split('/')[4])
    except Exception as e:
        raise InternalServerError(status=HTTPStatus.BAD_REQUEST, user_message='Improper PDF ID/NUM.', cause=repr(e))
    helper: PDFHelper = self.pocket.get(DICT_NAME)
    page_path = helper.get_page_path(pdf_id, page_num)
    if page_path is None:
        raise InternalServerError(status=HTTPStatus.BAD_REQUEST, user_message='Page not found.')

    # prepare html
    self.response.set_response_code(200)
    self.response.add_header("Content-type", "text/html")

    prev_page_button = f'<a href="/pdf/page/{pdf_id}/{page_num-1}" class="button green">Prev</a>' \
        if page_num > 0 else ''
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
    self.response.append_data(bytes(html, "utf-8"))


def get_pdf_image(self: MyHTTPHandler):
    try:
        pdf_id = int(self.path.split('/')[3])
        pdf_id = str(pdf_id)
        page_num = int(self.path.split('/')[4])
    except Exception:
        self.response.set_response_code(403)
        return
    helper: PDFHelper = self.pocket.get(DICT_NAME)
    page_path = helper.get_page_path(pdf_id, page_num)
    if page_path is None:
        self.response.set_response_code(403)
        return
    self.response.set_response_code(200)
    self.response.add_header('Content-type', 'image/jpg')
    with open(page_path, 'rb') as f:
        self.response.append_data(f.read())


def get_raw_pdf(self: MyHTTPHandler):
    try:
        pdf_id = int(self.path.split('/')[3])
        pdf_id = str(pdf_id)
    except Exception as e:
        raise InternalServerError(status=HTTPStatus.BAD_REQUEST, user_message='Improper PDF ID.', cause=repr(e))
    helper: PDFHelper = self.pocket.get(DICT_NAME)
    pdf_path = helper.get_pdf_path(pdf_id)
    if not pdf_path.exists():
        raise InternalServerError(status=HTTPStatus.BAD_REQUEST, user_message='ID does not exist.')
    self.response.set_response_code(200)
    self.response.add_header('Content-type', 'application/pdf')
    with open(pdf_path, 'rb') as f:
        self.response.append_data(f.read())


def get_database_status(self: MyHTTPHandler):
    path = [subpath for subpath in self.path.split('/')[3:] if subpath != '']
    helper: PDFHelper = self.pocket.get(DICT_NAME)
    if len(path) == 0:
        resp = os.listdir(helper.output_dir_path)
    elif len(path) == 1:
        pdf_id = str(int(path[0]))
        pages = helper.get_number_of_pages(pdf_id)
        size = os.path.getsize(helper.get_pdf_path(pdf_id))
        resp = {'pages': pages, 'size': size}
    else:
        raise InternalServerError(status=HTTPStatus.NOT_FOUND, user_message='Improper path URI.')
    self.response.set_response_code(200)
    self.response.add_header('Content-type', 'application/json')
    self.response.append_data(json.dumps(resp).encode('utf-8'))
