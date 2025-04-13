from __future__ import annotations

import sys
import contextlib
from types import ModuleType
from typing import TYPE_CHECKING
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import PathFinder, ModuleSpec

if TYPE_CHECKING:
    from typing import Any
    from collections.abc import Iterable, Sequence, Generator, Iterator

__author__ = "Dhia Hmila"
__version__ = "0.3.1"


class _LazyImports:
    def __init__(self) -> None:
        self._modules: set[str] = set()
        self.__objects: dict[str, dict[str, int]] = {}
        self._catchall = False

    def set_catchall(self, value):
        self._catchall = value

    def __contains__(self, x: str) -> bool:
        return self._catchall or x in self._modules

    def __getitem__(self, item: str) -> dict[str, int]:
        return self.__objects.get(item, {})

    def __iter__(self) -> Iterator[str]:
        yield from self._modules
        yield from (
            f"{mod}:{obj}#{count}" if count >= 0 else f"{mod}:{obj}"
            for mod, objs in self.__objects.items()
            for obj, count in objs.items()
        )

    def submodule(self, name: str) -> set[str]:
        prefix = name + "."
        return {mod[len(prefix) :] for mod in self._modules if mod.startswith(prefix)}

    def clear(self) -> None:
        self._modules.clear()
        self.__objects.clear()

    def add(self, value: str) -> None:
        obj = None
        if ":" in value:
            value, obj = value.split(":", 1)

        self._modules.add(value)
        if obj:
            obj, count = obj.split("#", 1) if "#" in obj else (obj, -1)

            mod_objects = self.__objects.setdefault(value, {})
            mod_objects[obj] = int(count) * 2

    def update(self, value: Iterable[str]) -> None:
        for v in value:
            self.add(v)


lazy_modules: _LazyImports = _LazyImports()

_INSTALLED = False
Undefined = object()
_LAZY_SUBMODULES = "lazy+submodules"
_LAZY_OBJECTS = "lazy+objects"


def _load_parent_module(fullname: str) -> None:
    if not (parent := ".".join(fullname.split(".")[:-1])):
        return

    if not (parent_module := sys.modules.get(parent)):
        return

    if isinstance(parent_module, LazyModule):
        _load_module(parent_module)


def _load_module(module: ModuleType) -> None:
    if not isinstance(module, LazyModule):
        return

    _load_parent_module(module.__name__)

    if (spec := module.__spec__) is None:
        return

    if (loader := spec.loader) is None:
        return

    if not hasattr(loader, "exec_module"):
        loader.load_module(module.__name__)
    else:
        loader.exec_module(module)


class LazyModule(ModuleType):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        setattr(self, _LAZY_SUBMODULES, lazy_modules.submodule(name))
        setattr(self, _LAZY_OBJECTS, lazy_modules[name])

    def __getattribute__(self, item: str) -> Any:
        if item in ("__doc__",):
            raise AttributeError(item)  # trigger loading

        return super().__getattribute__(item)

    def __getattr__(self, item: str) -> Any:
        if item in ("__path__", "__file__", "__cached__"):
            raise AttributeError(item)

        if item in getattr(self, _LAZY_SUBMODULES):
            raise AttributeError(item)

        if count := getattr(self, _LAZY_OBJECTS).get(item):
            getattr(self, _LAZY_OBJECTS)[item] = count - 1
            return LazyObjectProxy(self, item)

        _load_module(self)

        return getattr(self, item)

    def __dir__(self) -> Iterable[str]:
        _load_module(self)
        return dir(self)

    def __setattr__(self, attr: str, value: Any) -> None:
        if attr in (
            "__path__",
            "__file__",
            "__cached__",
            "__loader__",
            "__package__",
            "__spec__",
            "__class__",
            _LAZY_SUBMODULES,
            _LAZY_OBJECTS,
        ):
            return super().__setattr__(attr, value)

        if isinstance(value, ModuleType):
            return super().__setattr__(attr, value)

        set_attribute = super().__setattr__
        _load_module(self)
        return set_attribute(attr, value)


class LazyLoaderWrapper(Loader):
    def __init__(self, loader: Loader) -> None:
        self.loader = loader
        self.is_lazy = True

    def create_module(self, spec: ModuleSpec) -> ModuleType:
        return LazyModule(spec.name)

    def exec_module(self, module: ModuleType) -> None:
        if self.is_lazy:
            self.is_lazy = False
            return None

        self._cleanup(module)
        return self.loader.exec_module(module)

    def _cleanup(self, module: ModuleType) -> None:
        if module.__spec__ is not None:
            module.__spec__.loader = self.loader
        if _LAZY_SUBMODULES in module.__dict__:
            delattr(module, _LAZY_SUBMODULES)
        module.__class__ = ModuleType


class LazyPathFinder(MetaPathFinder):
    def __init__(self, module_names: _LazyImports) -> None:
        self.lazy_modules = module_names
        self.finder = PathFinder()

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None = None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        if fullname not in self.lazy_modules:
            _load_parent_module(fullname)

            return None

        spec = self.finder.find_spec(fullname, path, target)
        if spec is None:
            return None

        if spec.loader is None:
            return None

        spec.loader = LazyLoaderWrapper(spec.loader)
        return spec


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
            _load_module(self.__module)
            super().__setattr__(
                "_LazyObjectProxy__lobj", getattr(self.__module, self.__name)
            )
        return self.__lobj


@contextlib.contextmanager
def lazy_imports(
    *modules: str, extend: bool = False, catchall=None
) -> Generator[None, None, None]:
    original_value = {*lazy_modules}
    catchall = not modules if catchall is None else catchall
    try:
        lazy_modules.set_catchall(catchall)
        if not extend:
            lazy_modules.clear()

        lazy_modules.update(modules)
        yield
    finally:
        lazy_modules.clear()
        lazy_modules.set_catchall(False)
        lazy_modules.update(original_value)


def install() -> None:
    global _INSTALLED  # noqa: PLW0603

    if _INSTALLED:
        return

    import os
    from importlib.metadata import entry_points

    env_modules = os.environ.get("PYTHON_LAZY_IMPORTS", "")
    lazy_modules.update(
        module.strip() for module in env_modules.split(",") if module.strip()
    )
    if sys.version_info >= (3, 10):
        eps = entry_points(group="lazyimports")
    else:
        eps = entry_points().get("lazyimports", [])

    lazy_modules.update(
        module.strip()
        for entry in eps
        for module in entry.value.split(",")
        if module.strip()
    )

    _INSTALLED = True
    sys.meta_path.insert(0, LazyPathFinder(lazy_modules))
