class BaseFeature:
    def __init__(self, data):
        self.data = data

    def calculate(self):
        """Override in subclass."""
        raise NotImplementedError
