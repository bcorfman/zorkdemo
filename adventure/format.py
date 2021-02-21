ESC = '\033'


def underline(text):
    return ESC + '[4m' + text + ESC + '[0m'


def black(text):
    return ESC + '[30m' + text + ESC + '[0m'


def red(text):
    return ESC + '[31m' + text + ESC + '[0m'


def green(text):
    return ESC + '[32m' + text + ESC + '[0m'


def yellow(text):
    return ESC + '[33m' + text + ESC + '[0m'


def blue(text):
    return ESC + '[34m' + text + ESC + '[0m'


def magenta(text):
    return ESC + '[35m' + text + ESC + '[0m'


def cyan(text):
    return ESC + '[36m' + text + ESC + '[0m'


def light_gray(text):
    return ESC + '[37m' + text + ESC + '[0m'


def dark_gray(text):
    return ESC + '[90m' + text + ESC + '[0m'


def light_red(text):
    return ESC + '[91m' + text + ESC + '[0m'


def light_green(text):
    return ESC + '[92m' + text + ESC + '[0m'


def light_yellow(text):
    return ESC + '[93m' + text + ESC + '[0m'


def light_blue(text):
    return ESC + '[94m' + text + ESC + '[0m'


def light_magenta(text):
    return ESC + '[95m' + text + ESC + '[0m'


def light_cyan(text):
    return ESC + '[92m' + text + ESC + '[0m'
