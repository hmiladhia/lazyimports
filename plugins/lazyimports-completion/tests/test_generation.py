from pathlib import Path

import pytest

from lazyimports_completion.analysis import auto_detect, LazyEntity


@pytest.fixture
def tests_path() -> Path:
    return Path(__file__).parent


def test_generation(tests_path):
    result = auto_detect(tests_path / "fake_package")

    expected = {
        str(LazyEntity.LazyExporter): {"fake_package.exporter"},
        str(LazyEntity.LazyObject): {"fake_package.exporter.submodule:World"},
    }

    assert result == expected
