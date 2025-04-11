import threading
import json

from utils import get_timestamp, print_message
from log import Log, Record
from constants import DEFAULT_LOG_MODE, LOG_DIR

class InputLogger(threading.Thread):

    def __init__(self, time_interval=10):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.interval = time_interval
        self.log = Log()

    def add_record(self, button, is_on_press, coordinates=[0.0, 0.0], timestamp=None):
        ts = timestamp if timestamp is not None else get_timestamp()
        record = Record(timestamp=ts, button=button, is_on_press=is_on_press, coordinates=coordinates)
        self.log.append_log(record)

    def save_log_every_timeframe(self, filename, mode=DEFAULT_LOG_MODE):
        threading.Timer(self.interval, self.save_log_every_timeframe, [filename]).start()
        self.save_log(LOG_DIR + filename, mode)

    def save_log(self, filename, mode=DEFAULT_LOG_MODE):
        ts = get_timestamp()
        if mode == 'json':
            filename = self.generate_filename(ts, filename, mode)
            self.save_json(filename)
            print_message("Save log to " + filename)
        elif mode == 'text':
            filename = self.generate_filename(ts, filename, mode)
            self.save_text(filename)
            print_message("Save log to " + filename)
        else:
            raise ValueError('No such log option')

        self.clear_buffer()

    def generate_filename(self, ts, filename, mode):
        if mode == 'json':
            extension = '.json'
        elif mode == 'text':
            extension = '.txt'
        else:
            raise ValueError('Option error for filename generation')

        filename = filename + '_' + ts + extension
        return filename

    def save_json(self, filename):
        with open(filename, 'w') as json_file:
            json.dump(self.log.to_json(), json_file)

    def save_text(self, filename):
        with open(filename, "w") as text_file:
            text_file.write(str(self.log))

    def clear_buffer(self):
        self.log = Log()

