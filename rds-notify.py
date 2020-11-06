import os
import re
import time
import logging
import socket
import unidecode
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RdsHandler(FileSystemEventHandler):
    def __init__(self, file_path, host="192.168.1.25", port=1234):
        FileSystemEventHandler.__init__(self)
        self.file_path = file_path
        self._host = host
        self._port = port
        self._regex = re.compile(r"^(?P<artist>.*) - (?P<title>.*)$")
        self._last_sent = time.time()

    def on_modified(self, event):
        if event.src_path == self.file_path:
            with open(event.src_path, mode='r', encoding='utf-8') as f:
                content = f.read()
                self.parse_content_then_send(content)
                f.close()
            self._last_sent = time.time()

    def get_path(self):
        return os.path.dirname(self.file_path)

    def send_message(self, message):
        #if time.time() - self._last_sent < 1:
        #    return          
        _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _sock.connect((self._host, self._port))
        _sock.send(message.encode())
        _sock.close()
        logging.info("MESSAGE SENT: {}".format(message.replace('\r\n', '')))

    def _get_groups(self, input) -> dict:
        try:
            matches = self._regex.match(input)
            return matches.groupdict()
        except:
            return dict()

    def parse_content_then_send(self, content):
        try:
            groups = self._get_groups(content)
            if len(groups) == 2:
                artist = unidecode.unidecode(groups['artist'])
                title = unidecode.unidecode(groups['title'])
                message = "TEXT=Teraz gramy: {0} - {1}\r\n".format(artist, title)
            else:
                message = "TEXT=Pomaranczowy telefon Super FM: 91 44 555 50\r\n"
            self.send_message(message)
        except Exception as e:
            logging.error(e)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')    
    rds_handler = RdsHandler("C:\\Users\\Protone\\Desktop\\rds_notify\\send.txt")
    observer = Observer()    
    observer.schedule(rds_handler, path=rds_handler.get_path(), recursive=False)
    observer.start()
    logging.info("HAPPY SENDING FROM: '{}'".format(rds_handler.file_path))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()