import os
from .item import Item
from .location import Location
from .output import ConsoleOutput
from .state import StateMachine


class Leaflet(Item):
    def __init__(self):
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
        super().__init__(name='leaflet', full_name='a leaflet', description=txt.rstrip(),
                         needs_held_to_be_examined=True, can_be_taken=True)

    def examine(self):
        return self.description


class Mailbox(Item, StateMachine):
    def __init__(self):
        Item.__init__(self, 'mailbox', full_name='a small mailbox', contains=[Leaflet()])
        StateMachine.__init__(self, states={'opened': self.open, 'closed': self.close}, initial='closed')

    def list_items(self):
        items = self.features['contains']
        length = len(items)
        if length == 0:
            return 'nothing.'
        elif length == 1:
            return items[0].description + '.'
        else:
            txt = 'There is '
            for i in range(length-3):
                txt += items[i].description + ', '
            for i in range(length-2):
                txt += items[i].description + ' and '
            txt += items[length-1].description + '.'
            return txt

    def open(self):
        if self.current_state == 'closed':
            self.switch_state('opened')
            return 'You open the mailbox, revealing a small leaflet.'
        else:
            return 'The mailbox is already open.'

    def close(self):
        if self.current_state == 'opened':
            self.switch_state('closed')
            return 'You close the mailbox.'
        else:
            return "That's already closed."

    def take(self):
        return 'What a concept!'


class BoardedDoor(Item):
    def __init__(self):
        super().__init__(name='door', hidden=True)

    def open(self):
        return 'The door cannot be opened.'

    def close(self):
        return "That's not something you can close."


class WelcomeMat(Item):
    def __init__(self):
        super().__init__(name='mat', full_name='a welcome mat',
                         description="A rubber mat saying 'Welcome to Zork!' lies by the door.", can_be_taken=True)

    def examine(self):
        return 'Welcome to Zork!'

    def open(self):
        return "That's not something you can open."

    def close(self):
        return "That's not something you can close."


class WestOfHouse(Location):
    def __init__(self):
        items = [Mailbox(), BoardedDoor(), WelcomeMat()]
        can_go = {'north': 'NorthOfHouse'}
        super().__init__(title='West of House', contains=items, accessible=can_go)

