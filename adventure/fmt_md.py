"""
Format Markdown
"""


def emphasize(text):
    return "*" + text + "*"


def strong(text):
    return "**" + text + "**"


def underline(text):
    """there really isn't an underline in markdown... it's just another strong"""
    return "__" + text + "__"
