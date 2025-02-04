from collections.abc import Generator

import pytest

import lazyimports


@pytest.fixture(autouse=True)
def _mock_imports() -> Generator[None, None, None]:
    import sys

    og_modules = sys.modules.copy()
    try:
        yield
    finally:
        sys.modules.clear()
        sys.modules.update(og_modules)


def test_lazy_package(capsys: pytest.CaptureFixture[str]) -> None:
    with lazyimports.lazy_imports("fake_package"):
        import fake_package

    captured = capsys.readouterr()
    assert captured.out == ""
    fake_package.hello()
    captured = capsys.readouterr()
    assert captured.out == "fake_package\nHello\n"


def test_eager_package(capsys: pytest.CaptureFixture[str]) -> None:
    import fake_package

    captured = capsys.readouterr()
    assert captured.out == "fake_package\n"
    fake_package.hello()
    captured = capsys.readouterr()
    assert captured.out == "Hello\n"


def test_lazy_module(capsys: pytest.CaptureFixture[str]) -> None:
    with lazyimports.lazy_imports("fake_package.submodule"):
        import fake_package.submodule

    captured = capsys.readouterr()
    assert captured.out == "fake_package\n"
    fake_package.submodule.hello()
    captured = capsys.readouterr()
    assert captured.out == "fake_package.submodule\nHello\n"


def test_lazy_module_with_parents(capsys: pytest.CaptureFixture[str]) -> None:
    with lazyimports.lazy_imports("fake_package", "fake_package.submodule"):
        import fake_package.submodule

    captured = capsys.readouterr()
    assert captured.out == ""

    fake_package.submodule.hello()
    captured = capsys.readouterr()
    assert captured.out == "fake_package\nfake_package.submodule\nHello\n"


def test_eager_module_with_lazy_siblings(capsys: pytest.CaptureFixture[str]) -> None:
    with lazyimports.lazy_imports("fake_package", "fake_package.submodule"):
        import fake_package.submodule
        import fake_package.anothermodule

    captured = capsys.readouterr()
    assert captured.out == "fake_package\nfake_package.anothermodule\n"

    fake_package.submodule.hello()
    captured = capsys.readouterr()
    assert captured.out == "fake_package.submodule\nHello\n"


def test_eager_module_eager_siblings_lazy_parent(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports("fake_package"):
        import fake_package.submodule
        import fake_package.anothermodule

    captured = capsys.readouterr()
    assert (
        captured.out
        == "fake_package\nfake_package.submodule\nfake_package.anothermodule\n"
    )

    fake_package.submodule.hello()
    captured = capsys.readouterr()
    assert captured.out == "Hello\n"



def test_lazy_module_set_value(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports("fake_package", "fake_package.submodule"):
        import fake_package.submodule as submodule


    captured = capsys.readouterr()
    assert captured.out == ""

    submodule.world = "world"
    captured = capsys.readouterr()
    assert (
        captured.out
        == "fake_package\nfake_package.submodule\n"
    )

    submodule.hello()
    captured = capsys.readouterr()
    assert captured.out == "Hello\n"


def test_from_import_module(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports("fake_package", "fake_package.submodule"):
        from fake_package import submodule


    captured = capsys.readouterr()
    assert captured.out == ""
    submodule.hello()
    captured = capsys.readouterr()
    assert captured.out == "fake_package\nfake_package.submodule\nHello\n"


def test_from_import_func(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports("fake_package", "fake_package.submodule"):
        from fake_package import hello


    captured = capsys.readouterr()
    assert captured.out == "fake_package\n"
    hello()
    captured = capsys.readouterr()
    assert captured.out == "Hello\n"


def test_lazy_subpackage(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports("fake_package", "fake_package.subpackage"):
        import fake_package.subpackage

    captured = capsys.readouterr()
    assert captured.out == ""
    fake_package.subpackage.hello()
    captured = capsys.readouterr()
    assert captured.out == "fake_package\nfake_package.subpackage\nHello\n"
