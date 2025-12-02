import contextlib
import sys
from collections.abc import Generator

from ._context import LazyImportContext, MType
from ._import_machinery import IMPORT_CONTEXT, LazyPathFinder
from ._modules import ExportModule, LazyModule
from ._proxy import LazyObjectProxy

__author__ = "Dhia Hmila"
__version__ = "0.5.1"
__all__ = [
    "ExportModule",
    "LazyModule",
    "LazyObjectProxy",
    "MType",
    "__author__",
    "__version__",
    "lazy_imports",
]


@contextlib.contextmanager
def lazy_imports(
    *module_roots: str | None, explicit: bool = False
) -> Generator[LazyImportContext, None, None]:
    install()

    new_context = LazyImportContext.from_entrypoints()
    token = IMPORT_CONTEXT.set(new_context)

    try:
        with new_context:
            new_context.set_explicit_mode(explicit)
            for module_root in module_roots:
                if module_root is None:
                    continue

                new_context.add_module(module_root)
            yield new_context
    finally:
        IMPORT_CONTEXT.reset(token)


def install() -> None:
    if any(isinstance(finder, LazyPathFinder) for finder in sys.meta_path):
        return

    lazy_import_context = LazyImportContext.from_entrypoints()

    IMPORT_CONTEXT.set(lazy_import_context)
    sys.meta_path.insert(0, LazyPathFinder(IMPORT_CONTEXT))
