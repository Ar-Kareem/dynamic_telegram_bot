import logging
import os
import json

from src.handlers.serve_pdf.helper import PDFHelper

from src.utils.simple_server.simple_server import MyHTTPHandler


logger = logging.getLogger(__name__)


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
    helper: PDFHelper = self.pocket.get(__name__)
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
    helper: PDFHelper = self.pocket.get(__name__)
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
    helper: PDFHelper = self.pocket.get(__name__)
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
    helper: PDFHelper = self.pocket.get(__name__)
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

