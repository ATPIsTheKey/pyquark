from typing import Union, Tuple


class ListObject(list):  # todo
    @property
    def head(self):
        return self[0]

    @property
    def tail(self):
        return self[1:]

    @property
    def is_nil(self):
        raise NotImplementedError
