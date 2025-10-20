from __future__ import annotations

import sys
from types import ModuleType
from typing import TYPE_CHECKING
from contextvars import ContextVar
from importlib.abc import Loader, MetaPathFinder

from ._context import MType, LazyImportContext
from ._modules import (
    LazyModule,
    ExportModule,
    LAZY_SUBMODULES_ATTR,
    LAZY_OBJECTS_ATTR,
    load_parent_module,
)

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from collections.abc import Sequence

IMPORT_CONTEXT: ContextVar[LazyImportContext] = ContextVar("lazy_import_context")


class LazyLoaderWrapper(Loader):
    def __init__(
        self,
        loader: Loader,
        module_type: MType,
        submodules: set[str],
        object_names: set[str],
    ) -> None:
        self.loader = loader
        self.is_lazy = MType.Lazy in module_type
        self.is_export = MType.Export in module_type
        self.submodules = submodules
        self.object_names = object_names

    def create_module(self, spec: ModuleSpec) -> ModuleType:
        if not self.is_lazy:
            return ExportModule(spec.name)

        module = LazyModule(spec.name)
        setattr(module, LAZY_SUBMODULES_ATTR, self.submodules)
        setattr(module, LAZY_OBJECTS_ATTR, self.object_names)
        return module

    def exec_module(self, module: ModuleType) -> None:
        if self.is_lazy:
            self.is_lazy = False
            return None

        self._cleanup(module)
        return self.loader.exec_module(module)

    def _cleanup(self, module: ModuleType) -> None:
        if module.__spec__ is not None:
            module.__spec__.loader = self.loader

        if not isinstance(module, LazyModule):
            return

        if LAZY_SUBMODULES_ATTR in module.__dict__:
            delattr(module, LAZY_SUBMODULES_ATTR)

        if LAZY_OBJECTS_ATTR in module.__dict__:
            delattr(module, LAZY_OBJECTS_ATTR)

        module.__class__ = ExportModule if self.is_export else ModuleType


class LazyPathFinder(MetaPathFinder):
    def __init__(self, import_context: ContextVar[LazyImportContext]) -> None:
        self._import_context = import_context

    @property
    def import_context(self) -> LazyImportContext:
        return self._import_context.get()

    def find_spec(
        self,
        fullname: str,
        path: Sequence[str] | None = None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        module_type = self.import_context.get_module_type(fullname)

        if module_type == MType.Regular:
            load_parent_module(fullname)

            return None

        spec = self._find_spec(fullname, path, target)
        if spec is None:
            return None

        if spec.loader is None:
            return None

        spec.loader = LazyLoaderWrapper(
            spec.loader,
            module_type,
            self.import_context.get_lazy_submodules(fullname, path=spec.origin),
            self.import_context[fullname],
        )
        return spec

    @staticmethod
    def _find_spec(
        fullname: str,
        path: Sequence[str] | None = None,
        target: ModuleType | None = None,
    ) -> ModuleSpec | None:
        for finder in sys.meta_path:
            if isinstance(finder, LazyPathFinder):
                continue

            if spec := finder.find_spec(fullname, path, target):
                return spec

        return None
