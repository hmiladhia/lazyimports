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

with lazyimports.lazy_imports("package", "package.submodule"):
    from package import submodule

submodule.hello()
```

### 2. Configuring via `pyproject.toml`

Define lazy-loaded modules and objects in pyproject.toml for package-based usage.

#### Standard configuration:

```toml
[project.entry-points.lazyimports]
"lazy_modules" = "package,package.submodule"
"lazy_functions" = "package:hello"
"lazy_objects" = "package:array,package:integer"
```

#### Poetry-based configuration:

```toml
[tool.poetry.plugins.lazyimports]
"lazy_modules" = "package,package.submodule"
"lazy_functions" = "package:hello"
"lazy_objects" = "package:array,package:integer"
```

💡 The keys (lazy_modules, lazy_functions, etc.) can be listed in any order, using comma-separated values.

The previous example is also equivalent to:

```toml
[project.entry-points.lazyimports]
"custom_key" = "package,package.submodule,package:hello,package:array,package:integer"
```


After defining the configuration, import modules as usual—no code modifications needed:

```python
from package import submodule
from package import hello
```

### 3. Using an Environment Variable (for Development)

Dynamically enable lazy imports by setting an environment variable:

```sh
export PYTHON_LAZY_IMPORTS="package,package.submodule,package:array,package:integer,package:hello"
python script.py
```
