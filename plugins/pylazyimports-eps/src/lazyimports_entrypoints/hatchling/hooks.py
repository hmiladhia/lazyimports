from __future__ import annotations

from hatchling.plugin import hookimpl

from .lazyimports_hook import LazyimportsHook


@hookimpl
def hatch_register_metadata_hook() -> type[LazyimportsHook]:
    return LazyimportsHook
