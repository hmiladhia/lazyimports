from pathlib import Path

import pytest

from lazyimports import LazyModules
from lazyimports.__main__ import auto_detect


@pytest.fixture
def tests_path() -> Path:
    return Path(__file__).parent


def test_generation(tests_path):
    lazy_modules = LazyModules()
    lazy_modules.update(auto_detect(tests_path / "fake_package"))

    result = ",".join(lazy_modules)
    expected = (
        "~fake_package.sc,fake_package.sc.submodule,fake_package.sc.submodule:World#2"
    )

    assert result == expected
