from copy import deepcopy
import collections
from typing import Dict, List, Any, Callable, Union


class QuarkNameError(Exception):
    def __init__(self, name: str):
        super().__init__(f'{name} is neither defined globally or locally.')


class EnvironmentStack:
    def __init__(self):
        self._environments: List[Dict] = [dict()]

    def push_new_top_environment(self):
        self._environments.append(dict())

    def pop_top_environment(self):
        self._environments.pop()

    def update_top_environment(self, name, val):
        self._environments[-1][name] = val

    def deep_search_name(self, name):
        for environment in reversed(self._environments):
            if name in environment.keys():
                return environment[name]
        else:
            print(name)
            print(self._environments)
            raise IndexError

    def contains_name_in_any_environment(self, name):
        for namespace in self._environments:
            if name in namespace.keys():
                return True
        else:
            return False

    @property
    def top_environment(self):
        return self._environments[-1]

    def copy(self):
        deepcopy(self._environments)


class CallStack:
    def __init__(self, items: Union[List[Any]] = None):
        self._items = items if items else []
        self._consumed = 0

    def append(self, item):
        self._items.append(item)

    def extend(self, iterable):
        self._items.extend(iterable)

    def consume(self):
        self._consumed += 1

    def pop_consumed(self):
        self._items = self._items[self._consumed:]

    def __getitem__(self, i):
        return self._items[i]

    def __iter__(self):
        return iter(self._items)

    def __bool__(self):
        return self._items == []

    def __len__(self):
        return len(self._items)


class EvaluationContext:
    def __init__(self):
        self.environment_stack = EnvironmentStack()
        self.call_stack = CallStack()

    def __getitem__(self, i):
        return (self.environment_stack, self.call_stack)[i]
