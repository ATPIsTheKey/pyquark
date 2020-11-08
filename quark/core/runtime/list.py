from quark.core.util.pytypehints import LiteralType
from quark.core.util.datastructs import FlattenedPair

from typing import Union, Tuple


class ListObject(FlattenedPair):
    def __init__(self, head: LiteralType, tail: Union['ListObject', None]):
        super().__init__(head, tail)

    @property
    def head(self):
        return self._left

    @property
    def tail(self):
        return self._right

    @property
    def is_nil(self):
        raise NotImplementedError
