import markdown


MARKDOWN_EXTENSIONS = [
    "nl2br",  # turn all single \n into <br/>
    "sane_lists",  # in case we ever do lists
    "smarty",  # fancier quotes and things
]


def markdown2html(text: str) -> str:
    """Do all our markdown -> html in one place"""
    return markdown.markdown(text, extensions=MARKDOWN_EXTENSIONS)
