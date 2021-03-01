import os
from .util import get_cwd


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
        with open(os.path.join(get_cwd(), 'data', location_file)) as f:
            txt = f.read()
            txt = txt.replace(r'\t', r'    ')
            self._text = txt.rstrip()
        self.items = kwargs['contains']
        self.accessible_locations = kwargs['accessible']

    @property
    def description(self):
        txt = '**' + self.title + '**\n'
        txt += self._text
        items = self.list_items()
        if items:
            txt += '\n' + items
        return txt

    def list_items(self):
        txt = ''
        if self.items:
            # drop items that have no full name or description, since they are "hidden" inside the
            # location description.
            items = [item for item in self.items if item.full_name or item.description]
            special_items, regular_items = partition(items, lambda x: x.description)
            if regular_items:
                txt += self._list_regular_items(regular_items)
            if special_items:
                if regular_items:
                    txt += '\n'
                for item in special_items:
                    txt += item.description
        return txt

    def _list_regular_items(self, regular_items):
        txt = 'There is '
        if len(regular_items) == 1:
            txt += regular_items[0].full_name + ' here.'
        elif len(regular_items) == 2:
            txt += regular_items[0].full_name + ' and ' + regular_items[1].full_name + ' here.'
        else:
            for i in range(len(regular_items) - 2):
                txt += regular_items[i].full_name + ', '
            txt += regular_items[-2].full_name + ', and '
            txt += regular_items[-1].full_name + ' here.'
        # list contained items, if any.
        for item in regular_items:
            if hasattr(item, 'list_items'):
                item_txt = item.list_items()
                if item_txt:
                    txt += item_txt
        return txt
