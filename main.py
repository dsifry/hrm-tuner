import sys
import os
import glob

from keyboard_logger import KeyboardLogger
from constants import ENABLE_KEYBOARD


def main(argv):
    action = argv[0]

    if action == "start":
        start_logger()
    elif action == "clean":
        clean_log()
    else:
        raise ValueError("wrong running option")


def start_logger():
    if ENABLE_KEYBOARD:
        KeyboardLogger().start()


def clean_log():
    file_list = glob.glob("./log/*")
    for file_path in file_list:
        try:
            os.remove(file_path)
        except:
            print("Error while deleting file : ", file_path)


if __name__ == "__main__":
    main(sys.argv[1:])
