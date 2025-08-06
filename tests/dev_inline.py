
class Item:

    def __init__(self, name: str):
        self._name: str = name
        self._names = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __lshift__(self, name: str):
        self.collect(name)
        print(self._names)
        return self

    @property
    def name(self):
        return self._name

    def collect(self, name: str, age: int = 0):
        self._names.append(name)
        print(name)
        return self

item = Item("")

item << "Judy" << "Abigail" << "Katelyn"