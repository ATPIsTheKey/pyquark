class Namespace:
    def __init__(self):
        self._name_dict = dict()

    def add(self, item: str):
        pass

    def update(self):
        pass

    def pop(self, item: str):
        pass

    def __getitem__(self, item: str):
        return self._name_dict[item]


class Interpreter:
    def __init__(self):
        self._namespace = ...

    def evaluate(self):
        pass
