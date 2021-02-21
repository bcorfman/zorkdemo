import os
import sys
from .output import ConsoleOutput
from .westofhouse import WestOfHouse
from .northofhouse import NorthOfHouse
from .format import underline


def cls():
    return os.system('cls' if os.name == 'nt' else 'clear')


class Adventure:
    def __init__(self):
        self.output = ConsoleOutput()
        self.locations = [WestOfHouse(), NorthOfHouse()]
        self.current_room = self.locations[0]
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

    def open(self, tokens):
        def cmd(item):
            return item.open()
        return self._open_or_close(cmd, tokens)

    def close(self, tokens):
        def cmd(item):
            return item.close()
        return self._open_or_close(cmd, tokens)

    def _open_or_close(self, cmd, tokens):
        txt = ''
        items = self.current_room.items + self.inventory
        count = len(tokens)
        for token in tokens:
            if count > 1:
                txt += f"{token}: "
            found = False
            for item in items:
                if item.name == token:
                    found = True
                    txt += cmd(item)
            else:
                if not found:
                    txt += "You can't see any such thing."
        return txt

    def list_inventory(self, tokens):
        txt = 'You are '
        length = len(self.inventory)
        if length == 0:
            txt += 'empty handed.'
        elif length == 1:
            txt += 'holding ' + self.inventory[0].full_name + '.'
        elif length == 2:
            txt += 'holding ' + self.inventory[0].full_name + ' and ' + self.inventory[1].full_name + '.'
        else:
            txt += 'holding '
            for i in range(length-3):
                txt += self.inventory[i].full_name + ', '
            for i in range(length-2):
                txt += self.inventory[i].full_name + ' and '
            txt += self.inventory[length-1].full_name + '.'
        return self.output.wrap(txt)

    def exit(self, tokens):
        result = ''
        while result != 'Y' and result != 'N':
            result = input('Are you sure you want to quit? (Y/N) ')
            result = result.strip().upper()
        if result == 'Y':
            sys.exit(0)

    def examine(self, tokens, items=None, examined=None, name_count=None):
        txt = ''
        if tokens:
            if len(tokens) > 1:
                txt += "You can't use multiple objects with that verb."
            items = items or (self.current_room.items + self.inventory)
            examined = examined or set()
            name_count = name_count or len(tokens)
            name = tokens.pop()
            txt = self._examine(name, items, examined, name_count)
            examined.update(items)
            if not txt:
                for item in items:
                    if hasattr(item, 'current_state') and item.current_state == 'opened':
                        items_inside = item.features['contains']
                        txt += self._examine(name, items_inside, examined, name_count)
                        examined.update(items_inside)
                        if txt:
                            break
            if not txt:
                txt += f"I don't see any {name} here."
        return txt.rstrip()

    def _examine(self, name, items, examined, name_count):
        txt = ''
        for item in items:
            if item not in examined and item.name == name:
                if item not in self.inventory and item.features.get('needs_held_to_be_examined'):
                    txt += f'(Taking the {item.name} first)\n'
                    self.take([item.name], None, None, None, False)
                if name_count == 1:
                    txt += item.examine()
                    break
                elif name_count > 1:
                    txt += f'{name}:\n{item.examine()}'
                    break
        return txt

    def take(self, names, items=None, searched=None, name_count=None, output=True):
        txt = ''
        if names:
            items = items or self.current_room.items
            searched = searched or set()
            name_count = name_count or len(names)
            name = names.pop(0)
            txt = self._take(name, items, searched, name_count, output)
            searched.update(items)
            if (not txt and output is True) or output is False:
                for item in items:
                    if hasattr(item, 'current_state') and item.current_state == 'opened':
                        items_inside = item.features['contains']
                        txt += self._take(name, items_inside, searched, name_count, output)
                        searched.update(items_inside)
            if not txt and output is True:
                txt += f"I don't see any {name} here."
            txt += self.take(names, items, None, name_count, output)
        return txt.rstrip()

    def _take(self, name, items, searched, name_count, output):
        txt = ''
        for item in items:
            if item not in searched and item.name == name:
                if hasattr(item, 'take') and output:
                    if name_count == 1:
                        txt += item.take()
                    else:
                        txt += f'{name}: {item.take()}.'
                elif item not in self.inventory and item.features.get('can_be_taken'):
                    idx = items.index(item)
                    if idx > -1:
                        i = items.pop(idx)
                        if hasattr(i, 'taken'):
                            i.taken()
                        self.inventory.append(i)
                        if output:
                            if name_count == 1:
                                txt += "Taken."
                            else:
                                txt += f'{name}: Taken.\n'
                            break
        return txt

    def look(self, tokens):
        return self.current_room.description

    def drop(self, tokens):
        name_count = len(tokens)
        txt = ''
        for token in tokens:
            if token in [item.name for item in self.current_room.items]:
                if name_count == 1:
                    txt += f'The {token} is already here.'
                else:
                    txt += f'{token}: The {token} is already here.\n'
                continue
            for item in self.inventory:
                if token == item.name:
                    idx = self.inventory.index(item)
                    if idx > -1:
                        i = self.inventory.pop(idx)
                        self.current_room.items.append(i)
                        if name_count == 1:
                            txt += 'Dropped.'
                        else:
                            txt += f'{item.name}: Dropped.\n'
                        break
            if not txt:
                if name_count == 1:
                    txt += f"I don't see any {token} here."
                else:
                    txt += f"{token}: I don't see any {token} here.\n"
        return txt.rstrip()  # gets rid of last line feed

    def _go(self, direction):
        new_loc = self.current_room.accessible_locations.get(direction)
        if new_loc:
            for loc in self.locations:
                if loc.__class__.__name__ == new_loc:
                    self.current_room = loc
                    txt = self.current_room.description
                    break
            else:
                txt = f'ERROR: Cannot access {new_loc}.'
        else:
            txt = "You can't go that way."
        return txt

    def go_north(self, tokens):
        return self._go('north')

    def go_south(self, tokens):
        return self._go('south')

    def go_east(self, tokens):
        return self._go('east')

    def go_west(self, tokens):
        return self._go('west')

    def execute(self, tokens):
        tokens = self.remove_articles(tokens)
        command = tokens.pop(0)
        for cmd, func in self.commands.items():
            if cmd == command:
                txt = func(tokens)
                break
        else:
            txt = f"I don't understand how to {command} something."
        return txt

    def start_game_loop(self):
        cls()
        print(underline('ZORK Demo'))
        print()
        print(self.current_room.description)
        print()
        input_text = ''
        try:
            while not input_text == 'quit' or input_text == 'exit':
                input_text = input('>')
                if not input_text:
                    continue
                tokens = input_text.split()
                print(self.execute(tokens))
                print()
        except (KeyboardInterrupt, EOFError):
            print()
            sys.exit(0)
