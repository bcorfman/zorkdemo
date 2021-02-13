from .location import Location


class NorthOfHouse(Location):
    def __init__(self):
        super().__init__(title='North of House', contains=[])
