from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
    from collections.abc import Iterator
    from ._modules import LazyModule

Undefined = object()


class LazyObjectProxy:
    __slots__ = ("__lobj", "__module", "__name")

    def __init__(self, module: LazyModule, name: str) -> None:
        super().__setattr__("_LazyObjectProxy__module", module)
        super().__setattr__("_LazyObjectProxy__name", name)
        super().__setattr__("_LazyObjectProxy__lobj", Undefined)

    # -- Attributes --
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return getattr(self.__obj, name)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__obj, name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self.__obj, name, value)

    def __delattr__(self, name: str) -> None:
        delattr(self.__obj, name)

    # -- Type --
    def __instancecheck__(self, cls: type) -> bool:
        return isinstance(self.__obj, cls)

    def __subclasscheck__(self, cls: type) -> bool:
        return issubclass(type(self.__obj), cls)

    @property
    def __class__(self) -> type:
        return self.__obj.__class__

    @property
    def __dict__(self) -> dict[str, Any]:
        return self.__obj.__dict__

    def __dir__(self) -> list[str]:
        return dir(self.__obj)

    # -- Repr --
    def __repr__(self) -> str:
        return repr(self.__obj)

    def __str__(self) -> str:
        return str(self.__obj)

    def __hash__(self) -> int:
        return hash(self.__obj)

    # -- Comparisons --
    def __bool__(self) -> bool:
        return bool(self.__obj)

    def __eq__(self, other):
        return self.__obj == other

    def __ne__(self, other):
        return self.__obj != other

    def __lt__(self, other):
        return self.__obj < other

    def __le__(self, other):
        return self.__obj <= other

    def __gt__(self, other):
        return self.__obj > other

    def __ge__(self, other):
        return self.__obj >= other

    # -- Binary --
    def __add__(self, other):
        return self.__obj + other

    def __sub__(self, other):
        return self.__obj - other

    def __mul__(self, other):
        return self.__obj * other

    def __truediv__(self, other):
        return self.__obj / other

    def __floordiv__(self, other):
        return self.__obj // other

    def __mod__(self, other):
        return self.__obj % other

    def __pow__(self, other):
        return self.__obj**other

    def __rshift__(self, other):
        return self >> other

    def __lshift__(self, other):
        return self << other

    def __and__(self, other):
        return self & other

    def __or__(self, other):
        return self | other

    def __xor__(self, other):
        return self ^ other

    # -- Unary --
    def __neg__(self):
        return -self.__obj

    def __pos__(self):
        return +self.__obj

    def __abs__(self):
        return abs(self.__obj)

    def __invert__(self):
        return ~self.__obj

    def __round__(self, n=None):
        return round(self.__obj, n)

    def __floor__(self):
        import math

        return math.floor(self.__obj)

    def __ceil__(self):
        import math

        return math.ceil(self.__obj)

    def __trunc__(self):
        import math

        return math.trunc(self.__obj)

    # -- Indexing --
    def __getitem__(self, key: str) -> Any:
        return self.__obj[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.__obj[key] = value

    def __delitem__(self, key: str) -> None:
        del self.__obj[key]

    def __len__(self) -> int:
        return len(self.__obj)

    def __iter__(self) -> Iterator[Any]:
        return iter(self.__obj)

    def __contains__(self, item: str) -> bool:
        return item in self.__obj

    # -- Callable --
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.__obj(*args, **kwargs)

    # -- Context Manager --
    def __enter__(self):
        return self.__obj.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        return self.__obj.__exit__(exc_type, exc_value, traceback)

    # -- Copy --
    def __copy__(self):
        import copy

        return copy.copy(self.__obj)

    def __deepcopy__(self, memo):
        import copy

        return copy.deepcopy(self.__obj, memo)

    # -- Pickle --
    def __getstate__(self):
        import pickle

        return pickle.dumps(self.__obj)

    # -- Weak Reference --
    def __weakref__(self):
        import weakref

        return weakref.ref(self.__obj)

    @property
    def __obj(self) -> Any:
        if self.__lobj is Undefined:
            from ._modules import load_module

            load_module(self.__module)
            super().__setattr__(
                "_LazyObjectProxy__lobj", getattr(self.__module, self.__name)
            )
        return self.__lobj
