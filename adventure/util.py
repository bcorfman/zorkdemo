import sys
import os


def get_cwd():
    try:
        wd = sys._MEIPASS
    except AttributeError:
        wd = os.getcwd()
    return wd

