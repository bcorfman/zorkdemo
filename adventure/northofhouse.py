from .location import Location


class NorthOfHouse(Location):
    def __init__(self):
        can_go = {'west': 'WestOfHouse'}
        super().__init__(title='North of House', contains=[], accessible=can_go)
