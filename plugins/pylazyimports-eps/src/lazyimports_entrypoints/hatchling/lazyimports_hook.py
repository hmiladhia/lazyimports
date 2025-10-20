from __future__ import annotations

from pathlib import Path
from typing import Any

from hatchling.builders.wheel import WheelBuilder, WheelBuilderConfig
from hatchling.metadata.plugin.interface import MetadataHookInterface

from lazyimports_entrypoints.analysis import auto_detect, LazyEntity

LAZY_OBJECTS_ENTRYPOINT = "lazyimports"
LAZY_EXPORTERS_ENTRYPOINT = "lazyexporters"


class LazyimportsHook(MetadataHookInterface):
    PLUGIN_NAME = "lazyimports"

    def update(self, metadata: dict[str, Any]) -> None:
        if not self.config.get("enabled", True):
            return None

        if not (packages := self.config.get("packages")):
            cfg: WheelBuilderConfig = WheelBuilder(self.root).config
            packages = cfg.packages

        root = Path(self.root)
        lazy_modules = auto_detect(root / rel_path for rel_path in packages)

        if not any(lazy_modules.values()):
            return

        # https://packaging.python.org/en/latest/specifications/entry-points/#data-model
        prefix = self.config.get("name_prefix", "")
        entry_points = metadata.setdefault("entry-points", {})
        lazyobjects_entry_points = entry_points.setdefault(LAZY_OBJECTS_ENTRYPOINT, {})

        lazyobjects_entry_points.update(
            {
                f"{prefix}{obj.replace(':', '-')}": obj
                for obj in lazy_modules.get(LazyEntity.LazyObject, {})
            }
        )

        lazyexporters_entry_points = entry_points.setdefault(
            LAZY_EXPORTERS_ENTRYPOINT, {}
        )
        lazyexporters_entry_points.update(
            {
                f"{prefix}{mod.replace(':', '-')}": mod
                for mod in lazy_modules.get(LazyEntity.LazyExporter, {})
            }
        )
