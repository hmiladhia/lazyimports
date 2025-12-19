from __future__ import annotations

import sys
from types import ModuleType
from typing import TYPE_CHECKING

from ._proxy import LazyObjectProxy, extract_eager_object

if TYPE_CHECKING:
    from typing import Any
    from collections.abc import Iterable

LAZY_SUBMODULES_ATTR = "lazy+submodules"
LAZY_OBJECTS_ATTR = "lazy+objects"


class ExportModule(ModuleType):
    def __getattribute__(self, item: str) -> Any:
        value = super().__getattribute__(item)

        if isinstance(value, LazyObjectProxy):
            setattr(self, item, value := extract_eager_object(value))

        return value


class LazyModule(ModuleType):
    def __getattribute__(self, item: str) -> Any:
        if item in ("__doc__",):
            raise AttributeError(item)  # trigger loading

        return super().__getattribute__(item)

    def __getattr__(self, item: str) -> Any:
        if item in ("__path__", "__file__", "__cached__"):
            raise AttributeError(item)

        if item in getattr(self, LAZY_SUBMODULES_ATTR):
            raise AttributeError(item)

        if item in getattr(self, LAZY_OBJECTS_ATTR):
            return LazyObjectProxy(self, item)

        load_module(self)

        return getattr(self, item)

    def __dir__(self) -> Iterable[str]:
        load_module(self)
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
            LAZY_SUBMODULES_ATTR,
            LAZY_OBJECTS_ATTR,
        ):
            return super().__setattr__(attr, value)

        if isinstance(value, ModuleType):
            return super().__setattr__(attr, value)

        set_attribute = super().__setattr__
        load_module(self)
        return set_attribute(attr, value)


def load_parent_module(fullname: str) -> None:
    if not (parent := ".".join(fullname.split(".")[:-1])):
        return

    if not (parent_module := sys.modules.get(parent)):
        return

    if isinstance(parent_module, LazyModule):
        load_module(parent_module)


def load_module(module: ModuleType) -> ModuleType:
    if not isinstance(module, LazyModule):
        return module

    load_parent_module(module.__name__)

    if (spec := module.__spec__) is None:
        return module

    if (loader := spec.loader) is None:
        return module

    if not hasattr(loader, "exec_module"):
        loader.load_module(module.__name__)
    else:
        loader.exec_module(module)

    return module
