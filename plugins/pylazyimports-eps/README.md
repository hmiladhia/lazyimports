# Hatch-Lazyimports

![PyPI](https://img.shields.io/pypi/v/hatch-lazyimports)
![PyPI - License](https://img.shields.io/pypi/l/hatch-lazyimports)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/hatch-lazyimports)
![Tests](https://github.com/hmiladhia/hatch-lazyimports/actions/workflows/quality.yaml/badge.svg)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

This plugin will automaticilly detect lazy imports that are under a `with lazy_imports()` statement.
It will then, fill the distribution's metadata related entry-point.

## Example

```toml
[project]
dependencies = ["auto-lazy-imports>=0.5.0"]
dynamic = ['entry-points', 'entry-points.lazyimports', 'entry-points.lazyexporters']

[build-system]
requires = ["hatchling", "hatch-lazyimports"]
build-backend = "hatchling.build"

[tool.hatch.metadata.hooks.lazyimports]
enabled = true
prefix = ""
```
