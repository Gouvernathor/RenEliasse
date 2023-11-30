import renpy # type: ignore
python_object = object
python_dict = dict

"""renpy
init python:
"""
import collections

class InsertableDictMixin(python_object):
    __slots__ = ()

    def insert(self, existing_key, new_key, value, *, before=True):
        """
        Similaire à list.insert pour des dict ordonnés.
        Insère la clé `new_key` avec la valeur `value` avant (par défaut) ou
        après `existing_key`.
        """

        if not self:
            self[new_key] = value
            return

        passed = False
        items = []
        for k in tuple(self):
            if passed:
                items.append((k, self.pop(k)))
            elif k == existing_key:
                if before:
                    items.append((k, self.pop(k)))
                passed = True

        self[new_key] = value

        for k, v in items:
            self[k] = v

    def insert_after(self, existing_key, new_key, value):
        return self.insert(existing_key, new_key, value, before=False)

# class LockableOrderedDict(collections.OrderedDict):
class LockableOrderedDict(python_dict, InsertableDictMixin):
    __slots__ = ("locked")

    def __init__(self, *args, **kwargs):
        self.locked = False
        super().__init__(*args, **kwargs)
        self.locked = bool(args or kwargs)

    def __setitem__(self, key, value, /):
        if self.locked and (key not in self):
            raise KeyError(f"{key} is not a valid key for this dict")
        return super().__setitem__(key, value)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        rv = super().fromkeys(iterable, value)
        rv.locked = True
        return rv

def locked_wrap(func):
    def wrapper(self, *args, **kwargs):
        if self.locked:
            raise Exception("Cannot remove an item from a locked dict")
        return func(self, *args, **kwargs)
    return wrapper

for fn in (
    "__delitem__",
    "pop",
    "popitem",
    "clear",
):
    setattr(LockableOrderedDict, fn, locked_wrap(getattr(dict, fn)))

del fn, locked_wrap
