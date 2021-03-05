import re


class MarkdownRE:
    def __init__(self):
        self.re_emphasis = re.compile(r'(\*)([^*]+)\1')
        self.re_strong = re.compile(r'(\*{2})(.+?)\1')
        self.re_underline = re.compile(r'(_{2})(.+?)\1')


class MarkdownToRich(MarkdownRE):
    def __init__(self):
        super().__init__()

    def transform(self, text):
        text = self.re_strong.sub(r'[yellow]\2[/yellow]', text)
        text = self.re_underline.sub(r'[underline]\2[/underline]', text)
        return text


class MarkdownPassthru:
    """Markdown raw passthru"""
    def transform(self, text: str) -> str:
        return text


class MarkdownToHTML(MarkdownRE):
    def __init__(self):
        super().__init__()

    def transform(self, text):
        text = self.re_strong.sub(r'<b>\2</b>', text)
        text = self.re_underline.sub(r'<u>\2</u>', text)
        return text
