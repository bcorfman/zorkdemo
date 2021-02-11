class Item:
    def __init__(self, name='', full_name='', description='', can_be_taken=True):
        if not name:
            self.name = self.__class__.__name__
        else:
            self.name = name
        self.full_name = full_name
        self.description = description
        self.can_be_taken = can_be_taken
        self.items = []
        self.opened = False
        self.needs_held_to_be_examined = False
        self.has_long_description = self.description is not None and self.description != ''

    def open(self):
        return "That's not something you can open."

    def examine(self):
        return f"I see nothing special about the {self.name}."