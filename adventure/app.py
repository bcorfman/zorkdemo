import os
import sys
from .output import ConsoleOutput
from .house import WestOfHouse


def cls():
    return os.system('cls' if os.name == 'nt' else 'clear')


class Adventure:
    def __init__(self):
        self.version = 0.1
        self.output = ConsoleOutput()
        self.rooms = [WestOfHouse()]
        self.current_room = self.rooms[0]
        self.inventory = []
        self.commands = {'examine': self.examine,
                         'read': self.examine,
                         'look': self.look,
                         'l': self.look,
                         'inventory': self.list_inventory,
                         'i': self.list_inventory,
                         'get': self.take,
                         'take': self.take,
                         'drop': self.drop,
                         'open': self.open,
                         'close': self.close,
                         'north': self.go_north,
                         'n': self.go_north,
                         'east': self.go_east,
                         'e': self.go_east,
                         'south': self.go_south,
                         's': self.go_south,
                         'west': self.go_west,
                         'w': self.go_west,
                         'exit': self.exit,
                         'quit': self.exit,
                         }

    def remove_articles(self, tokens):
        articles = ['the', 'a', 'an', 'and']
        remaining_tokens = [tokens[0]]
        for i in range(1, len(tokens)):
            if tokens[i] not in articles:
                remaining_tokens.append(tokens[i])
        return remaining_tokens

    def start_game_loop(self):
        cls()
        self.output.print(f'ZORK Demo')
        self.output.print('Written by Brandon Corfman')
        self.output.print('')
        print(self.current_room.description)
        print(self.current_room.list_items())
        input_text = ''
        while not input_text == 'quit' or input_text == 'exit':
            self.output.print('')
            input_text = input('>')
            tokens = self.remove_articles(input_text.split())
            command = tokens[0]
            for cmd, func in self.commands.items():
                if cmd == command:
                    func(tokens[1:])
                    break
            else:
                self.output.print(f"I don't understand how to {command} something.")

    def open(self, tokens):
        items = self.current_room.items + self.inventory
        for token in tokens:
            for item in items:
                if item.name == token:
                    self.output.print(item.open())

    def close(self, tokens):
        items = self.current_room.items + self.inventory
        for token in tokens:
            for item in items:
                if item.name == token:
                    print(item.close())

    def examine(self, names, items=None, examined=None, name_count=None):
        if not names:
            return
        if items is None:
            items = self.current_room.items + self.inventory
        if examined is None:
            examined = set()
        if name_count is None:
            name_count = len(names)
        name = names.pop()
        found = self._examine(name, items, examined, name_count)
        examined.update(items)
        if not found:
            for item in items:
                if item.opened:
                    found = self._examine(name, item.items, examined, name_count)
                    examined.update(item.items)
        if not found:
            self.output.print(f"I don't see any {name} here.")
        self.examine(names, items, examined, name_count)

    def _examine(self, name, items, examined, name_count):
        found = False
        for item in items:
            if item not in examined and item.name == name:
                found = True
                if item not in self.inventory and item.needs_held_to_be_examined:
                    self.output.print(f'(Taking the {item.name} first)')
                if name_count == 1:
                    print(item.examine())
                else:
                    self.output.print(f'{name}: {item.examine()}')
        return found

    def list_inventory(self, tokens):
        txt = 'You are '
        length = len(self.inventory)
        if length == 0:
            txt += 'empty handed.'
        elif length == 1:
            txt += 'holding ' + self.inventory[0].description
        else:
            for i in range(length-3):
                txt += self.inventory[i].description + ', '
            for i in range(length-2):
                txt += self.inventory[i].description + ' and '
            txt += self.inventory[length-1].description + '.'
        self.output.print(txt)

    def exit(self, tokens):
        result = ''
        while result != 'Y' and result != 'N':
            result = input('Are you sure you want to quit? (Y/N) ')
            result = result.strip().upper()
        if result == 'Y':
            sys.exit(0)

    def take(self, tokens, output=True):
        for item in tokens:
            # TODO: Needs to be recursive.
            idx = self.current_room.items.index(item)
            if idx > -1:
                i = self.current_room.items.pop(idx)
                self.inventory.append(i)
                print(f'{i.name}: taken.')
            else:
                print(f"I don't see {item.name} here.")

    def _take(self, token, output=True):
        pass

    def look(self, tokens):
        pass

    def drop(self, tokens):
        for item in tokens:
            idx = self.inventory.index(item)
            if idx > -1:
                i = self.inventory.pop(idx)
                self.current_room.items.append(i)
                print(f'{i.name}: dropped\n.')
            else:
                print(f"The {item.name} is already here.")

    def go_north(self, tokens):
        pass

    def go_south(self, tokens):
        pass

    def go_east(self, tokens):
        pass

    def go_west(self, tokens):
        pass


