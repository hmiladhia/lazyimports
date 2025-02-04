# Lazyimports

[![logo](https://raw.githubusercontent.com/hmiladhia/lazyimports/refs/heads/main/docs/linelogo.png)](https://pypi.org/project/auto-lazy-imports/)

[![PyPI](https://img.shields.io/pypi/v/auto-lazy-imports)](https://pypi.org/project/auto-lazy-imports/)
[![PyPI - License](https://img.shields.io/pypi/l/auto-lazy-imports)](https://pypi.org/project/auto-lazy-imports/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/auto-lazy-imports)](https://pypi.org/project/auto-lazy-imports/)
![Tests](https://github.com/hmiladhia/lazyimports/actions/workflows/quality.yaml/badge.svg)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Overview 🌐

**Lazyimports** is a Python module that enables lazy imports using native Python syntax, reducing startup time and improving performance by delaying module loading until needed.

## Installation 🔨

Install `lazyimports` via pip:

```sh
pip install auto-lazy-imports
```

## Usage 👍

### 1. Using a `with` Statement

Wrap imports in a `with` statement to enable lazy loading:

```python
import lazyimports

with lazyimports.lazy_modules("package", "package.submodule"):
    from package import submodule

submodule.hello()
```

### 2. Configuring via `pyproject.toml`

For package-based usage, define lazy-loaded modules in `pyproject.toml`:

#### Standard configuration:

```toml
[project.entry-points.lazyimports]
"my_package" = "package,package.submodule"
```

#### Poetry-based configuration:

```toml
[tool.poetry.plugins.lazyimports]
"my_package" = "package,package.submodule"
```

### 3. Using an Environment Variable (for Development)

Set an environment variable to enable lazy loading dynamically:

```sh
export PYTHON_LAZY_IMPORTS="package,package.submodule"
python script.py
```
