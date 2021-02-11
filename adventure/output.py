import shutil
import textwrap


class ConsoleOutput:
    def __init__(self):
        self.console_size = shutil.get_terminal_size()
        self.wrapper = textwrap.TextWrapper(width=self.console_size.columns-1)

    def wrap(self, line):
        return self.wrapper.fill(line)

    def wrap_lines(self, lines):
        output = []
        for line in lines:
            if not line:
                output.append('')
            else:
                output.append(self.wrapper.fill(line))
        return output

    def print_lines(self, lines):
        for line in self.wrap_lines(lines):
            print(line)

    def print(self, line):
        print(self.wrap(line))
