from __future__ import annotations

import pkgutil
from copy import copy
from enum import Flag, auto
from typing import TYPE_CHECKING
from importlib.metadata import entry_points


if TYPE_CHECKING:
    import sys

    if sys.version_info < (3, 11):
        from typing_extensions import Self
    else:
        from typing import Self

    from types import TracebackType
    from collections.abc import Iterable

LAZY_OBJECTS_ENTRYPOINT = "lazyimports"
LAZY_EXPORTERS_ENTRYPOINT = "lazyexporters"


class MType(Flag):
    Regular = 0
    Lazy = auto()
    Export = auto()


class LazyImportContext:
    def __init__(self) -> None:
        self._is_active: bool = False
        self._explicit_mode: bool = False
        self._lazy_modules: set[str] = set()
        self._sc_modules: set[str] = set()
        self._objects: dict[str, str] = {}

    def __enter__(self) -> Self:
        self._is_active = True
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        self._is_active = False

    def __copy__(self) -> Self:
        ctx = LazyImportContext()
        ctx._is_active = self._is_active
        ctx._explicit_mode = self._explicit_mode
        ctx._lazy_modules = copy(self._lazy_modules)
        ctx._sc_modules = copy(self._sc_modules)
        ctx._objects = copy(self._objects)

        return ctx

    @classmethod
    def from_entrypoints(cls) -> Self:
        ctx = cls()

        for obj in (
            object_id.strip()
            for entry in entry_points(group=LAZY_OBJECTS_ENTRYPOINT)
            for object_id in entry.value.split(",")
            if object_id.strip()
        ):
            modname, _, object_name = obj.partition(":")
            ctx.add_objects(modname, object_name)

        for entry in entry_points(group=LAZY_EXPORTERS_ENTRYPOINT):
            ctx.add_module(entry.value.strip(), module_type=MType.Export)

        return ctx

    def set_explicit_mode(self, value: bool = True) -> None:
        self._explicit_mode = value

    def get_module_type(self, fullname: str) -> MType:
        module_type = MType.Export if fullname in self._sc_modules else MType.Regular

        if self._is_active and self._is_lazy_module(fullname):
            return module_type | MType.Lazy

        return module_type

    def get_lazy_submodules(self, fullname: str, path: str | None = None) -> set[str]:
        prefix = fullname + "."
        submodules = {
            mod[len(prefix) :] for mod in self._lazy_modules if mod.startswith(prefix)
        }

        if self._explicit_mode:
            return submodules

        if path:
            submodules.update(
                info.name for info in pkgutil.iter_modules([path], prefix=prefix)
            )
        return submodules

    def __getitem__(self, fullname: str) -> set[str]:
        return self._objects.get(fullname, set())

    def add_module(self, fullname: str, module_type: MType = MType.Lazy) -> None:
        if MType.Lazy in module_type:
            self._lazy_modules.add(fullname)

        if MType.Export in module_type:
            self._sc_modules.add(fullname)

    def add_objects(self, fullname: str, names: str | Iterable[str]) -> None:
        if isinstance(names, str):
            names = (names,)

        mod_objects = self._objects.setdefault(fullname, set())
        mod_objects.update(names)

    def _is_lazy_module(self, fullname: str) -> bool:
        if self._explicit_mode:
            return fullname in self._lazy_modules

        return fullname in self._lazy_modules or any(
            fullname.startswith(module_root + ".") for module_root in self._lazy_modules
        )
