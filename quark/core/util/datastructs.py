from typing import Union


class FlattenedPair:
    def __init__(self, left, right):
        self._left = left
        self._right = right
        self._has_nested = isinstance(right, FlattenedPair)

    def __getitem__(self, i):
        if i == 0:
            return self._left
        else:
            return self._right[i - 1] if self._has_nested else self._right

    def __setitem__(self, i, val):
        if i == 0:
            self._left = val
        else:
            if self._has_nested:
                self._right[i - 1] = val
            else:
                if i == 1:
                    self._right = val
                else:
                    raise IndexError()

    def __len__(self):
        if self._has_nested:
            return 1 + len(self._right) if self._right else 1
        else:
            return 2 if self._right else 1

    def __iter__(self):
        yield self._left
        if self._has_nested:
            yield from self._right
        else:
            if self._right:
                yield self._right

    def __str__(self):
        return f"{','.join(self)}]"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__str__()})"


if __name__ == '__main__':
    flattened_pair = FlattenedPair(1, FlattenedPair(2, 3))
    for e in flattened_pair:
        print(e)
