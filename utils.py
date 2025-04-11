import datetime

def get_timestamp():
    now = datetime.datetime.now()
    ts = now.strftime('%Y%m%d_%H%M%S')
    return ts

def print_message(msg):
    ts = get_timestamp()
    print("[" + ts + "]: " + msg)