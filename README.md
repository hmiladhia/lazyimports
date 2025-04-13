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

with lazyimports.lazy_imports(catchall=True):
    from package import submodule

submodule.hello()
```

Note: With catchall enabled, all modules under the with statement will be lazily loaded. However, you can also explicitly specify which packages to load lazily by providing them as arguments.
This is especially useful, if you want to use lazy objects

```python
import lazyimports

with lazyimports.lazy_imports("package:function", "package.subpackage"):
    import package.subpackage
    from package import function

package.subpackage.hello()
function()
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

## Advanced Usage 🧑‍🏫

### 1. Counted Lazy objects

Sometimes you want to use have limit the lazy imports of a certain object to your package. In that cas, you can use counted Lazy objects, which will only lazy import an object a limited number of times.

```python
import lazyimports

with lazyimports.lazy_imports("package:function#3"):
    import package
    from package import function # Lazily Imported: Counter decremented by 2 ( from ... import syntax)

    package.function # Lazily Imported: Counter decremented by 1 (attribute access syntax)

    from package import function # Eagerly Imported: Counter reached 0

function()
```

### 2. Shortcut Collection Module

Shortcut collection modules are a special kind of modules, that will import lazy objects from other modules to provide an import shortcut.

If you import a lazy object from a shortcut collection, it will trigger an automatic import.

Here is a common pattern using counted lazy objects and shortcut collection modules:

```bash
├───my_package
│   ├───submodule1.py
│   ├───submodule2.py
│   └───__init__.py
└───main.py
```

```python
# my_package/__init__.py

from lazyimports import lazy_imports, lazy_modules

lazy_modules.add("~my_package") # could also be defined in pyproject.toml

with lazy_imports("my_package.submodule1:MyClass1#2", "my_package.submodule2:MyClass2#2"):
    from .submodule1 import MyClass1
    from .submodule2 import MyClass2

__all__ = ["MyClass1", "MyClass2"]
```

```python
# main.py

from my_package import MyClass2

# MyClass2 is eagerly loaded ( you do not get a proxy but the real class ),
# but MyClass1 won't be loaded until it is also imported
```
