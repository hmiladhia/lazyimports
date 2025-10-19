import sys
import contextlib
from collections.abc import Generator


from ._proxy import LazyObjectProxy
from ._modules import LazyModule, ExportModule
from ._context import MType, LazyImportContext
from ._import_machinery import LazyPathFinder, IMPORT_CONTEXT


__author__ = "Dhia Hmila"
__version__ = "0.5.0"
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

    try:
        token = IMPORT_CONTEXT.set(new_context)
        with new_context:
            new_context.set_explicit_mode(explicit)
            for module_root in module_roots:
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
