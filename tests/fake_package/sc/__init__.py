"""DocStrings."""

from lazyimports import lazy_imports

with lazy_imports():
    from .submodule import World

print(__name__)


__all__ = ["World"]
