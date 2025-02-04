from __future__ import annotations

import sys
import contextlib
from types import ModuleType
from typing import TYPE_CHECKING
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import PathFinder, ModuleSpec

if TYPE_CHECKING:
    from typing import Any
    from collections.abc import Iterable, Sequence, Generator

__author__ = "Dhia Hmila"
__version__ = "0.0.1"

lazy_modules: list[str] = []

_LAZY_SUBMODULES = "++lazy-submodules++"

def _load_parent_module(fullname: str) -> None:
    if not (parent := ".".join(fullname.split(".")[:-1])):
        return

    if not (parent_module := sys.modules.get(parent)):
        return

    if isinstance(parent_module, LazyModule):
        _load_module(parent_module)


def _load_module(module: ModuleType) -> None:
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

        prefix = name + "."
        lazy_submodules = {mod[len(prefix):] for mod in lazy_modules if mod.startswith(prefix)}
        setattr(self, _LAZY_SUBMODULES, lazy_submodules)

    def __getattribute__(self, item: str) -> Any:  # noqa ANN401
        if item in ("__doc__",):
            raise AttributeError(item)  # trigger loading

        return super().__getattribute__(item)

    def __getattr__(self, item: str) -> Any:  # noqa ANN401
        if item in ("__path__", "__file__", "__cached__"):
            raise AttributeError(item)

        if item in getattr(self, _LAZY_SUBMODULES):
            raise AttributeError(item)

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
        self.please_load = False

    def create_module(self, spec: ModuleSpec) -> ModuleType:
        # mod = self.loader.create_module(spec)
        return LazyModule(spec.name)

    def exec_module(self, module: ModuleType) -> None:
        if not self.please_load:
            self.please_load = True
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
    def __init__(self, module_names: list[str]) -> None:
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


@contextlib.contextmanager
def lazy_imports(*modules: str) -> Generator[None, None, None]:
    original_value = lazy_modules[:]

    try:
        lazy_modules.extend(modules)
        yield
    finally:
        lazy_modules[:] = original_value


def install() -> None:
    sys.meta_path.insert(0, LazyPathFinder(lazy_modules))


install()
