import os
from .item import Item
from .location import Location
from .output import ConsoleOutput


class Leaflet(Item):
    def __init__(self):
        self.needs_held_to_be_examined = True
        with open(os.path.join('data', 'leaflet.txt')) as f:
            text = '    '
            self._paragraphs = []
            for line in f.readlines():
                if line.strip() == '':
                    self._paragraphs.append(text)
                    text = '    '
                else:
                    if text.strip() == '' and self._paragraphs:  # append a blank line before every paragraph
                        self._paragraphs.append('')
                    text += line.strip() + ' '
            if text.strip():  # add whatever text is at the end.
                self._paragraphs.append(text)
        txt = ''
        for line in ConsoleOutput().wrap_lines(self._paragraphs):
            txt += line + '\n'
        super().__init__('leaflet', 'a leaflet', txt.rstrip())

    def examine(self):
        return self.description


class Mailbox(Item):
    def __init__(self):
        super().__init__('mailbox', 'a small mailbox', None, False)
        self.items = [Leaflet()]
        self.opened = False

    def list_items(self):
        length = len(self.items)
        if length == 0:
            return 'nothing.'
        elif length == 1:
            return self.items[0].description + '.'
        else:
            txt = 'There is '
            for i in range(length-3):
                txt += self.items[i].description + ', '
            for i in range(length-2):
                txt += self.items[i].description + ' and '
            txt += self.items[length-1].description + '.'
            return txt

#    def examine(self):
#        length = len(self.items)
#        if length > 0 and self.opened:
#            return 'The mailbox contains ' + self.list_items()
#        elif length == 0 and self.opened:
#            return 'The mailbox is empty.'
#        else:
#            return 'I see nothing special about the mailbox.'

    def open(self):
        if not self.opened:
            self.opened = True
            return 'You open the mailbox, revealing a small leaflet.'
        else:
            return 'The mailbox is already open.'


class BoardedDoor(Item):
    def __init__(self):
        super().__init__('door', None, None, False)

    def open(self):
        return 'The door cannot be opened.'


class WelcomeMat(Item):
    def __init__(self):
        super().__init__('mat', 'a welcome mat', "A rubber mat saying 'Welcome to Zork!' lies by the door.", True)

    def examine(self):
        return 'Welcome to Zork!'


class WestOfHouse(Location):
    def __init__(self):
        with open(os.path.join('data', 'WestOfHouse.desc')) as f:
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
        items = [Mailbox(), BoardedDoor(), WelcomeMat()]
        super().__init__('West of House', txt.rstrip(), items)

    def remove_item(self, item):
        pass

    def add_item(self, item):
        pass
