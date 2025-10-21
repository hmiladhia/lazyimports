from pathlib import Path

import pytest

from lazyimports_entrypoints.analysis import auto_detect, LazyEntity


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
