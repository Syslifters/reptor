class Base:
    def __init__(self, **kwargs):
        self.notename = kwargs.get('notename')

    @classmethod
    def add_arguments(cls, parser):
        pass

    def run(self):
        pass
