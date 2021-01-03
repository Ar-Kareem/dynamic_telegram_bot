import logging
import threading
import time

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

logger = logging.getLogger(__name__)

def thread(updater):
    logging.info('thread started')
    global_flags = updater.dispatcher.bot_data['global_flags']
    start_time = global_flags['starttime']

    http_queue = []
    global_flags['http_queue'] = http_queue
    http_server = start_server(http_queue)
    last_checked_length = 0
    while True:
        time.sleep(0.125)
#         logging.info(f"Thread in loop: {global_flags['terminate_flag']}, Start time: {start_time}")
        if len(http_queue) > last_checked_length:
            last_checked_length = len(http_queue)
            updater.bot.send_message(chat_id=global_flags['my_chat_id'], text=http_queue[-1])
        if global_flags['terminate_flag']:
            # Terminate thread
            http_server.shutdown()
            http_server.server_close()
            break

def init_handlers(updater):
    # create daemon thread
    t = threading.Thread(target=thread, args=(updater,))
    t.daemon = True
    t.start()
    
    
    
    
    
    
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import socket
import json

class MyHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, outside_world):
        self.outside_world = outside_world

    def __call__(self, *args, **kwargs):
        """ Handle a request """
        super().__init__(*args, **kwargs)
        
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.outside_world.append(self.path)

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        self._set_headers()
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.end_headers()
        js_data = json.loads(self.data_string)
#         print("{}".format(js_data))
        self.outside_world.append(js_data)

def my_serve_forever(server):
    server.serve_forever()
        
def start_server(outside_world):
#     hostName = "localhost"
    hostName = socket.gethostname()
    serverPort = 8049
    handler = MyHTTPHandler(outside_world)
    webServer = HTTPServer((hostName, serverPort), handler)
    
    thread = threading.Thread(target = my_serve_forever, args=(webServer,))
    thread.daemon = True
    thread.start()
    return webServer
