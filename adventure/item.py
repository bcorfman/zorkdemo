class Item:
    def __init__(self, name, **kwargs):
        self.name = name
        self.features = kwargs.copy()
        if not self.features.get('contains'):
            self.features['contains'] = []

    @property
    def full_name(self):
        return self.features.get('full_name')

    @property
    def description(self):
        return self.features.get('description')

    def examine(self):
        return f'I see nothing special about the {self.name}.'
