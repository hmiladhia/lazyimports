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
__version__ = "0.2.0"


class _LazyImports:
    def __init__(self) -> None:
        self._modules: set[str] = set()
        self._objects: dict[str, set[str]] = {}

    def __contains__(self, x: str) -> bool:
        return x in self._modules

    def __getitem__(self, item: str) -> set[str]:
        return self._objects.get(item, set())

    def __iter__(self) -> Iterator[str]:
        yield from self._modules
        yield from (
            f"{mod}:{obj}" for mod, objs in self._objects.items() for obj in objs
        )

    def submodule(self, name: str) -> set[str]:
        prefix = name + "."
        return {mod[len(prefix) :] for mod in self._modules if mod.startswith(prefix)}

    def clear(self) -> None:
        self._modules.clear()
        self._objects.clear()

    def add(self, value: str) -> None:
        obj = None
        if ":" in value:
            value, obj = value.split(":", 1)

        self._modules.add(value)
        if obj:
            self._objects.setdefault(value, set()).add(obj)

    def update(self, value: Iterable[str]) -> None:
        for v in value:
            self.add(v)


lazy_modules: _LazyImports = _LazyImports()

_INSTALLED = False
Undefined = object()
_LAZY_SUBMODULES = "lazy+submodules"
_LAZY_CALLABLES = "lazy+callables"


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
        setattr(self, _LAZY_CALLABLES, lazy_modules[name])

    def __getattribute__(self, item: str) -> Any:  # noqa ANN401
        if item in ("__doc__",):
            raise AttributeError(item)  # trigger loading

        return super().__getattribute__(item)

    def __getattr__(self, item: str) -> Any:  # noqa ANN401
        if item in ("__path__", "__file__", "__cached__"):
            raise AttributeError(item)

        if item in getattr(self, _LAZY_SUBMODULES):
            raise AttributeError(item)

        if item in getattr(self, _LAZY_CALLABLES):
            return LazyObjectProxy(self, item)

        _load_module(self)

        return getattr(self, item)

    def __dir__(self) -> Iterable[str]:
        _load_module(self)
        return dir(self)

    def __setattr__(self, attr: str, value: Any) -> None:  # noqa ANN401
        if attr in (
            "__path__",
            "__file__",
            "__cached__",
            "__loader__",
            "__package__",
            "__spec__",
            "__class__",
            _LAZY_SUBMODULES,
            _LAZY_CALLABLES,
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
        self.to_be_loaded = True

    def create_module(self, spec: ModuleSpec) -> ModuleType:
        return LazyModule(spec.name)

    def exec_module(self, module: ModuleType) -> None:
        if self.to_be_loaded:
            self.to_be_loaded = False
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
    __slots__ = ("__module", "__name", "__lobj")

    def __init__(self, module: LazyModule, name: str) -> None:
        super().__setattr__("_LazyObjectProxy__module", module)
        super().__setattr__("_LazyObjectProxy__name", name)
        super().__setattr__("_LazyObjectProxy__lobj", Undefined)

    def __getattr__(self, name: str) -> Any:  # noqa ANN401
        return getattr(self.__obj, name)

    def __setattr__(self, name: str, value: Any) -> None:  # noqa ANN401
        setattr(self.__obj, name, value)

    def __delattr__(self, name: str) -> None:
        delattr(self.__obj, name)

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

    def __repr__(self) -> str:
        return repr(self.__obj)

    def __str__(self) -> str:
        return str(self.__obj)

    def __bool__(self) -> bool:
        return bool(self.__obj)

    def __eq__(self, other: Any) -> bool:  # noqa ANN401
        return self.__obj == other

    def __hash__(self) -> int:
        return hash(self.__obj)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # noqa ANN401
        return self.__obj(*args, **kwargs)

    def __getattribute__(self, name: str) -> Any:  # noqa ANN401
        try:
            return super().__getattribute__(name)
        except AttributeError:
            return getattr(self.__obj, name)

    def __getitem__(self, key: str) -> Any:  # noqa ANN401
        return self.__obj[key]

    def __setitem__(self, key: str, value: Any) -> None:  # noqa ANN401
        self.__obj[key] = value

    def __delitem__(self, key: str) -> None:
        del self.__obj[key]

    def __len__(self) -> int:
        return len(self.__obj)

    def __iter__(self) -> Iterator[Any]:
        return iter(self.__obj)

    def __contains__(self, item: str) -> bool:
        return item in self.__obj

    @property
    def __obj(self) -> Any:  # noqa ANN401
        if self.__lobj is Undefined:
            _load_module(self.__module)
            super().__setattr__(
                "_LazyObjectProxy__lobj", getattr(self.__module, self.__name)
            )
        return self.__lobj


@contextlib.contextmanager
def lazy_imports(*modules: str, extend: bool = False) -> Generator[None, None, None]:
    original_value = {*lazy_modules}

    try:
        if not extend:
            lazy_modules.clear()

        lazy_modules.update(modules)
        yield
    finally:
        lazy_modules.clear()
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
