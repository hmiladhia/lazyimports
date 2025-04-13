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
        import fake_package.submodule as submodule  # noqa: PLR0402

    captured = capsys.readouterr()
    assert captured.out == ""

    submodule.world = "world"
    captured = capsys.readouterr()
    assert captured.out == "fake_package\nfake_package.submodule\n"

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


def test_lazy_object(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports("fake_package:hello"):
        from fake_package import hello

    captured = capsys.readouterr()
    assert captured.out == ""
    hello()
    captured = capsys.readouterr()
    assert captured.out == "fake_package\nHello\n"


def test_lazy_object_array(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports("fake_package.submodule:array"):
        from fake_package.submodule import array

    captured = capsys.readouterr()
    assert captured.out == "fake_package\n"
    array.append("value")
    captured = capsys.readouterr()
    assert captured.out == "fake_package.submodule\n"


def test_lazy_object_integer(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports("fake_package", "fake_package.submodule:integer"):
        from fake_package.submodule import integer

    captured = capsys.readouterr()
    assert captured.out == ""
    print(integer)
    captured = capsys.readouterr()
    assert captured.out == "fake_package\nfake_package.submodule\n1\n"

    assert integer == 1
    assert integer is not 1  # noqa: F632

    from fake_package.submodule import integer

    assert integer is 1  # noqa: F632


def test_lazy_object_ge(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports("fake_package", "fake_package.submodule:integer"):
        from fake_package.submodule import integer

    captured = capsys.readouterr()
    assert captured.out == ""
    assert integer >= 0
    captured = capsys.readouterr()
    assert captured.out == "fake_package\nfake_package.submodule\n"


def test_catchall(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports(catchall=True):
        import json
        import fake_package

    captured = capsys.readouterr()
    assert captured.out == ""
    print(json.dumps(fake_package.array))
    captured = capsys.readouterr()
    assert captured.out == "fake_package\n[]\n"


def test_counted_proxy_objects_1(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports("fake_package:World#2"):
        from fake_package import World

    captured = capsys.readouterr()
    assert captured.out == ""

    with lazyimports.lazy_imports("fake_package:World#27"):
        from fake_package import World

    captured = capsys.readouterr()
    assert captured.out == "fake_package\n"

    World()


def test_counted_proxy_objects_2(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports("fake_package:World#4"):
        from fake_package import World
        from fake_package import World  # noqa: F811

        captured = capsys.readouterr()
        assert captured.out == ""

        from fake_package import World  # noqa: F811

        captured = capsys.readouterr()
        assert captured.out == "fake_package\n"

        World()


def test_counted_proxy_objects_3(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports("fake_package:World#4"):
        import fake_package
        from fake_package import World

        _ = fake_package.World
        _ = fake_package.World

        captured = capsys.readouterr()
        assert captured.out == ""

        from fake_package import World  # noqa: F811

        captured = capsys.readouterr()
        assert captured.out == "fake_package\n"

        World()


def test_shortcut_collection(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports(
        "~fake_package.sc", "fake_package.sc.submodule:World"
    ):
        import fake_package.sc

    captured = capsys.readouterr()
    assert captured.out == "fake_package\nfake_package.sc\n"

    assert isinstance(fake_package.sc.submodule.World, lazyimports.LazyObjectProxy)
    assert not isinstance(fake_package.sc.World, lazyimports.LazyObjectProxy)

    captured = capsys.readouterr()
    assert captured.out == "fake_package.sc.submodule\n"


def test_non_shortcut_collection(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with lazyimports.lazy_imports("fake_package.sc.submodule:World"):
        import fake_package.sc

    captured = capsys.readouterr()
    assert captured.out == "fake_package\nfake_package.sc\n"

    assert isinstance(fake_package.sc.submodule.World, lazyimports.LazyObjectProxy)
    assert isinstance(fake_package.sc.World, lazyimports.LazyObjectProxy)

    captured = capsys.readouterr()
    assert captured.out == ""

    fake_package.sc.World()

    captured = capsys.readouterr()
    assert captured.out == "fake_package.sc.submodule\nWorld\n"
