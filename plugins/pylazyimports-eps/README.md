# Pylazyimports-entrypoints

![PyPI](https://img.shields.io/pypi/v/pylazyimports-eps)
![PyPI - License](https://img.shields.io/pypi/l/pylazyimports-eps)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/pylazyimports-eps)
![Tests](https://github.com/hmiladhia/lazyimports/actions/workflows/quality.yml/badge.svg)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

This plugin will automaticilly detect lazy imports that are under a `with lazy_imports()` statement.
It will then, fill the distribution's metadata related entry-point.

## Example

```toml
[project]
dependencies = ["pylazyimports>=0.5.0"]
dynamic = ['entry-points', 'entry-points.lazyimports', 'entry-points.lazyexporters']

[build-system]
requires = ["hatchling", "pylazyimports-eps"]
build-backend = "hatchling.build"

[tool.hatch.metadata.hooks.lazyimports]
enabled = true
prefix = ""
```
