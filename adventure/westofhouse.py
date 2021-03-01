import os
from .item import Item
from .location import Location
from .output import MarkdownToRich
from .state import StateMachine
from .util import get_cwd


class Leaflet(Item):
    def __init__(self):
        self.formatter = MarkdownToRich()
        with open(os.path.join(get_cwd(), 'data', 'leaflet.txt')) as f:
            txt = f.read()
            txt = txt.replace(r'\t', r'    ')
        super().__init__(name='leaflet', full_name='a small leaflet', contents=txt.rstrip(),
                         needs_held_to_be_examined=True, can_be_taken=True)

    def examine(self):
        markdown = self.features['contents']
        return self.formatter.transform(markdown)


class Mailbox(Item, StateMachine):
    def __init__(self):
        Item.__init__(self, 'mailbox', full_name='a small mailbox', contains=[Leaflet()])
        StateMachine.__init__(self, states={'opened': self.open, 'closed': self.close}, initial='closed')

    def list_items(self):
        txt = ''
        items = self.features['contains'] if self.current_state == 'opened' else []
        length = len(items)
        indent = ' ' * 4
        if length > 0:
            txt += '\nThe mailbox contains:\n'
            if length == 1:
                txt += indent + items[0].full_name.capitalize() + '.'
            elif length == 2:
                txt += indent + items[0].full_name.capitalize() + ' and ' + items[1].full_name + ' here.'
            else:
                txt += indent
                for i in range(length-3):
                    txt += items[i].full_name.capitalize() + ', '
                for i in range(length-2):
                    txt += items[i].full_name + ' and '
                txt += items[length-1].full_name + ' here.'
        return txt

    def open(self):
        if self.current_state == 'closed':
            self.switch_state('opened')
            if self.features.get('contains'):
                txt = 'You open the mailbox, revealing a small leaflet.'
            else:
                txt = 'You open the mailbox.'
        else:
            txt = 'The mailbox is already open.'
        return txt

    def close(self):
        if self.current_state == 'opened':
            self.switch_state('closed')
            txt = 'You close the mailbox.'
        else:
            txt = "That's already closed."
        return txt

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

    def taken(self):
        self.description = ""


class WestOfHouse(Location):
    def __init__(self):
        items = [Mailbox(), BoardedDoor(), WelcomeMat()]
        can_go = {'north': 'NorthOfHouse'}
        super().__init__(title='West of House', contains=items, accessible=can_go)
