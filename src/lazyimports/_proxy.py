from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from typing import Any
    from types import ModuleType
    from collections.abc import Iterator
    from ._modules import LazyModule

T = TypeVar("T")
_LAZY_ORIGIN_KEY = "__lazyorigin__"


class LazyObjectProxy:
    __slots__ = (_LAZY_ORIGIN_KEY,)

    def __init__(self, module: LazyModule, name: str) -> None:
        _set_lazy_origin(self, (module, name))

    # -- Attributes --
    def __getattr__(self, name: str) -> Any:
        return getattr(extract_eager_object(self), name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(extract_eager_object(self), name, value)

    def __delattr__(self, name: str) -> None:
        delattr(extract_eager_object(self), name)

    # -- Type --
    def __instancecheck__(self, cls: type) -> bool:
        return isinstance(extract_eager_object(self), cls)

    def __subclasscheck__(self, cls: type) -> bool:
        return issubclass(type(extract_eager_object(self)), cls)

    @property
    def __class__(self) -> type:
        return extract_eager_object(self).__class__

    @property
    def __dict__(self) -> dict[str, Any]:
        return extract_eager_object(self).__dict__

    def __dir__(self) -> list[str]:
        return dir(extract_eager_object(self))

    # -- Repr --
    def __repr__(self) -> str:
        return repr(extract_eager_object(self))

    def __str__(self) -> str:
        return str(extract_eager_object(self))

    def __hash__(self) -> int:
        return hash(extract_eager_object(self))

    # -- Comparisons --
    def __bool__(self) -> bool:
        return bool(extract_eager_object(self))

    def __eq__(self, other):
        return extract_eager_object(self) == other

    def __ne__(self, other):
        return extract_eager_object(self) != other

    def __lt__(self, other):
        return extract_eager_object(self) < other

    def __le__(self, other):
        return extract_eager_object(self) <= other

    def __gt__(self, other):
        return extract_eager_object(self) > other

    def __ge__(self, other):
        return extract_eager_object(self) >= other

    # -- Binary --
    def __add__(self, other):
        return extract_eager_object(self) + other

    def __sub__(self, other):
        return extract_eager_object(self) - other

    def __mul__(self, other):
        return extract_eager_object(self) * other

    def __truediv__(self, other):
        return extract_eager_object(self) / other

    def __floordiv__(self, other):
        return extract_eager_object(self) // other

    def __mod__(self, other):
        return extract_eager_object(self) % other

    def __pow__(self, other):
        return extract_eager_object(self) ** other

    def __rshift__(self, other):
        return extract_eager_object(self) >> other

    def __lshift__(self, other):
        return extract_eager_object(self) << other

    def __and__(self, other):
        return extract_eager_object(self) & other

    def __or__(self, other):
        return extract_eager_object(self) | other

    def __xor__(self, other):
        return extract_eager_object(self) ^ other

    # -- Unary --
    def __neg__(self):
        return -extract_eager_object(self)

    def __pos__(self):
        return +extract_eager_object(self)

    def __abs__(self):
        return abs(extract_eager_object(self))

    def __invert__(self):
        return ~extract_eager_object(self)

    def __round__(self, n=None):
        return round(extract_eager_object(self), n)

    def __floor__(self):
        import math

        return math.floor(extract_eager_object(self))

    def __ceil__(self):
        import math

        return math.ceil(extract_eager_object(self))

    def __trunc__(self):
        import math

        return math.trunc(extract_eager_object(self))

    # -- Indexing --
    def __getitem__(self, key: str) -> Any:
        return extract_eager_object(self)[key]

    def __setitem__(self, key: str, value: Any) -> None:
        extract_eager_object(self)[key] = value

    def __delitem__(self, key: str) -> None:
        del extract_eager_object(self)[key]

    def __len__(self) -> int:
        return len(extract_eager_object(self))

    def __iter__(self) -> Iterator[Any]:
        return iter(extract_eager_object(self))

    def __contains__(self, item: str) -> bool:
        return item in extract_eager_object(self)

    # -- Callable --
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return extract_eager_object(self)(*args, **kwargs)

    # -- Context Manager --
    def __enter__(self):
        return extract_eager_object(self).__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        return extract_eager_object(self).__exit__(exc_type, exc_value, traceback)

    # -- Copy --
    def __copy__(self):
        import copy

        return copy.copy(extract_eager_object(self))

    def __deepcopy__(self, memo):
        import copy

        return copy.deepcopy(extract_eager_object(self), memo)

    # -- Pickle --
    def __getstate__(self):
        import pickle

        return pickle.dumps(extract_eager_object(self))

    # -- Weak Reference --
    def __weakref__(self):
        import weakref

        return weakref.ref(extract_eager_object(self))


def _get_lazy_origin(
    lazy_proxy_object: LazyObjectProxy,
) -> tuple[ModuleType, str] | tuple[Any]:
    return object.__getattribute__(lazy_proxy_object, _LAZY_ORIGIN_KEY)


def _set_lazy_origin(
    lazy_proxy_object: LazyObjectProxy, value: tuple[ModuleType, str] | tuple[Any]
) -> None:
    object.__setattr__(
        lazy_proxy_object,
        _LAZY_ORIGIN_KEY,
        value,
    )


# The typing is intentionally misleading for it to work properly for the user
def extract_eager_object(lazy_proxy_object: T) -> T:
    if not isinstance(lazy_proxy_object, LazyObjectProxy):
        return lazy_proxy_object

    match _get_lazy_origin(lazy_proxy_object):
        case (module, name):
            from ._modules import load_module

            _set_lazy_origin(
                lazy_proxy_object,
                (lobject := getattr(load_module(module), name),),
            )
        case (lobject,):
            pass

    return lobject
