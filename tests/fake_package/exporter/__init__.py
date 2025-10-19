"""DocStrings."""

from lazyimports import lazy_imports

with lazy_imports(__package__) as ctx:
    ctx.add_objects(f"{__package__}.submodule", "World")

    from .submodule import World

print(__name__)


__all__ = ["World"]
