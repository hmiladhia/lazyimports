import ast
from pathlib import Path

import pytest

from lazyimports_entrypoints.analysis import (
    auto_detect,
    LazyEntity,
    get_aliases_from_tree,
)


@pytest.fixture
def tests_path() -> Path:
    return Path(__file__).parent


def test_generation(tests_path: Path):
    result = auto_detect(tests_path / "fake_package")

    expected = {
        LazyEntity.LazyExporter: {"fake_package.exporter"},
        LazyEntity.LazyObject: {"fake_package.exporter.submodule:World"},
    }

    assert result == expected


def test_alias_extraction(tests_path: Path):
    code = tests_path.joinpath("fake_package/exporter/submodule.py").read_text(
        encoding="utf8"
    )
    tree = ast.parse(code)
    result = get_aliases_from_tree(tree)

    expected = ({"lazyimports", "lazy"}, {"lazy_imports", "lazyimports"})

    assert result == expected
