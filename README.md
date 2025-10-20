# Lazyimports

[![logo](https://raw.githubusercontent.com/hmiladhia/lazyimports/refs/heads/main/docs/linelogo.png)](https://pypi.org/project/auto-lazy-imports/)

[![PyPI](https://img.shields.io/pypi/v/auto-lazy-imports)](https://pypi.org/project/auto-lazy-imports/)
[![PyPI - License](https://img.shields.io/pypi/l/auto-lazy-imports)](https://pypi.org/project/auto-lazy-imports/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/auto-lazy-imports)](https://pypi.org/project/auto-lazy-imports/)
![Tests](https://github.com/hmiladhia/lazyimports/actions/workflows/quality.yaml/badge.svg)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-orange.json)](https://github.com/copier-org/copier)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Overview 🌐

**Lazyimports** is a Python module that enables lazy imports using native Python syntax, reducing startup time by delaying module loading until needed and help export public API without losing auto-completion/linting.

## Installation 🔨

Install `lazyimports` via pip:

```sh
pip install pylazyimports
```

## Usage 👍

### 1. Using a `with` Statement

Wrap imports in a `with` statement and add at least a package name to enable lazy loading. All of its submodules will also be lazy loaded.

```python
import lazyimports

with lazyimports.lazy_imports("package"):
    from package import submodule

submodule.hello()
```

💡 Note: With the `explicit` option enabled, all modules and submodules have to be specified explicitly for them to be lazy imported. Use this when you want more control.

```python
import lazyimports

with lazyimports.lazy_imports("package", "package.subpackage", explicit=True):
    import package.subpackage

package.subpackage.hello()
```

### 2. Lazy Objects

To load `objects`/`functions`/`classes` lazily, you need to add them to the import context:

```python
with lazyimports.lazy_imports("package") as ctx:
    ctx.add_objects("package", "function")

    from package import function

result = function()
```

### 3. Configuring via `pyproject.toml`

Define lazy-loaded modules and objects in pyproject.toml for package-based usage.

#### Standard configuration - PEP 621

```toml
[project.entry-points.lazyimports]
"lazy_function" = "package:function"
"lazy_array" = "package:array"
"lazy_integer" = "package:integer"
```

#### Poetry-based configuration

```toml
[tool.poetry.plugins.lazyimports]
"lazy_function" = "package:function"
"lazy_array" = "package:array"
"lazy_integer" = "package:integer"
```

After defining the configuration, import lazy objects with no need to add them to the context as they are automatically added:

```python
with lazyimports.lazy_imports("package"):
    from package import function
```

## Advanced Usage 🧑‍🏫

### 1. Re-export Modules

`Re-Export` modules are a special kind of modules, that will import lazy objects from other modules to provide an import "shortcut" ( or in other terms to re-export them again).

This is a common pattern when writing your own package, if you have too many modules and want to expose a simple public api in the `__init__.py` file.

If you import a lazy object from a `re-export` module, it will trigger an automatic import and the the user will get the **real** object not a `LazyObjectProxy`. This is great if you want your package to behave with packages like `pydantic`.

Here is a common pattern using counted lazy objects and shortcut collection modules:

```bash
├─── my_package
│   ├───submodule1.py
│   ├───submodule2.py
│   └───__init__.py
├─── pyproject.toml
└─── main.py
```

```python
# my_package/__init__.py

from lazyimports import lazy_imports

with lazy_imports(__package__):
    from .submodule1 import MyClass1
    from .submodule2 import MyClass2

__all__ = ["MyClass1", "MyClass2"]
```

```toml
# pyproject.toml

[project.entry-points.lazyimports]
"my_package.submodule1-MyClass1" = "my_package.submodule1:MyClass1"
"my_package.submodule2-MyClass2" = "my_package.submodule1:MyClass2"

[project.entry-points.lazyexporters]
"my_package_any_name" = "my_package"
```

```python
# main.py

from my_package import MyClass2

# MyClass2 is eagerly loaded ( you do not get a proxy but the real class ),
# but MyClass1 won't be loaded until it is also imported
```

#### Alternate version

If you are not creating a package, you can achieve the same thing without the `pyproject.toml` entry-points.

```python
# main.py

from lazyimports import lazy_imports, MType

with lazy_imports() as ctx:  # No module is passed, there is no lazy importing involved.
    ctx.add_module("my_package", MType.Export)

    from my_package import MyClass2

# MyClass2 is eagerly loaded ( you do not get a proxy but the real class ),
# but MyClass1 won't be loaded until it is also imported
```

### 2. Filling entry-points automatically

You do not have to fill the `entry-points` yourself, as it may be tedious to do every time you change your package. You can use build-plugins to fill them for you.

For example, if you add `hatch-lazyimports` to your build system ( and enable it ), the plugin will analyze your code and add the lazy objects under a `with lazy_imports()` statement in the `entry-points` section.

```toml
[project]
dependencies = ["pylazyimports>=0.1.0"]
dynamic = ['entry-points', 'entry-points.lazyimports', 'entry-points.lazyexporters']

[build-system]
requires = ["hatchling", "pylazyimports-eps"]
build-backend = "hatchling.build"

[tool.hatch.metadata.hooks.lazyimports]
enabled = true
```

⚠️ So far, only `hatchling` is supported.
