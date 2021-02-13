import os
from .output import ConsoleOutput
from .format import yellow


def partition(seq, fn):
    """Partitions one sequence into two sequences, by testing whether each element
    satisfies fn or not. """
    pos, neg = [], []
    for elt in seq:
        if fn(elt):
            pos.append(elt)
        else:
            neg.append(elt)
    return pos, neg


class Location:
    def __init__(self, **kwargs):
        self.title = kwargs['title']
        location_file = self.__class__.__name__ + '.txt'
        with open(os.path.join('data', location_file)) as f:
            text = ''
            title = f.readline().strip()
            paragraphs = [title]
            for line in f.readlines():
                if line.strip() == '':
                    paragraphs.append(text)
                    text = ''
                else:
                    text += line
            if text.strip():  # add whatever text is at the end.
                paragraphs.append(text)
        txt = ''
        for line in ConsoleOutput().wrap_lines(paragraphs):
            txt += line + '\n'
        self._text = txt.rstrip()
        self.items = kwargs['contains']

    @property
    def description(self):
        txt = yellow(self.title) + '\n'
        txt += self._text + '\n'
        txt += self.list_items()
        return txt

    def list_items(self):
        txt = ''
        if self.items:
            # drop items that have no full name or description, since they are "hidden" inside the
            # location description.
            items = [item for item in self.items if item.full_name or item.description]
            special_items, regular_items = partition(items, lambda x: x.description)
            if regular_items:
                txt = 'There is '
                if len(regular_items) == 1:
                    txt += regular_items[0].full_name + ' here.'
                elif len(regular_items) == 2:
                    txt += regular_items[0].full_name + ' and ' + regular_items[1].full_name + ' here.'
                else:
                    for i in range(len(regular_items)-2):
                        txt += regular_items[i].full_name + ', '
                    txt += regular_items[-2].full_name + ', and '
                    txt += regular_items[-1].full_name + '.'
            if special_items:
                if regular_items:
                    txt += '\n'
                for item in special_items:
                    txt += item.description
        return txt
