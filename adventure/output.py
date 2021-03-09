import re


class MarkdownRE:
    def __init__(self):
        self.re_emphasis = re.compile(r"(\*)([^*]+)\1")
        self.re_strong = re.compile(r"(\*{2})(.+?)\1")
        self.re_underline = re.compile(r"(_{2})(.+?)\1")


class MarkdownToRich(MarkdownRE):
    def __init__(self):
        super().__init__()

    def transform(self, text):
        text = self.re_strong.sub(r"[yellow]\2[/yellow]", text)
        text = self.re_underline.sub(r"[underline]\2[/underline]", text)
        return text


class MarkdownPassthru:
    """Markdown [mostly] raw passthru"""

    def transform(self, text: str) -> str:
        new_lines = []
        for line in text.split("\n"):
            new_lines.append(
                line.strip()
            )  # md freaks out about leading/trailing spaces!
        return "\n".join(new_lines)


class MarkdownToHTML(MarkdownRE):
    def __init__(self):
        super().__init__()

    def transform(self, text):
        text = self.re_strong.sub(r"<b>\2</b>", text)
        text = self.re_underline.sub(r"<u>\2</u>", text)
        return text
