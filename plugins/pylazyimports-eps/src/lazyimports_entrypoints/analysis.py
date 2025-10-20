import ast
from pathlib import Path
from enum import StrEnum
from collections.abc import Generator, Iterable


class LazyEntity(StrEnum):
    LazyObject = "lazy-objects"
    LazyImports = "lazy-imports"
    LazyExporter = "lazy-exporter"


def auto_detect(paths: Iterable[str | Path] | str | Path) -> dict[LazyEntity, set[str]]:
    if isinstance(paths, str | Path):
        paths = [paths]

    entities = (
        entity for path in paths for entity in auto_detect_from_path(Path(path))
    )

    results = {}
    for entity_type, entity in entities:
        results.setdefault(entity_type, set()).add(entity)

    return results


def auto_detect_from_path(path: Path) -> Generator[tuple[LazyEntity, str], None, None]:
    module_paths = (path,) if path.is_file() else path.glob("**/*.py")

    for module_path in module_paths:
        content = module_path.read_text(encoding="utf-8")
        name = (
            module_path.with_suffix("")
            .relative_to(path.parent)
            .as_posix()
            .replace("/", ".")
            .replace(".__init__", "")
        )
        yield from from_module_content(name, content)


def from_module_content(
    fullname: str, content: str
) -> Generator[tuple[LazyEntity, str], None, None]:
    tree = ast.parse(content)

    for with_body in with_from_tree(tree):
        yield LazyEntity.LazyExporter, fullname
        yield from imports_from_tree(fullname, with_body)


def with_from_tree(tree: ast.AST) -> Generator[ast.stmt]:
    for node in ast.walk(tree):
        if isinstance(node, ast.With):
            if not any(is_lazy_import(item.context_expr) for item in node.items):
                continue

            yield from node.body


def is_lazy_import(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False

    if node.keywords:
        return False

    func = node.func

    return (isinstance(func, ast.Name) and func.id == "lazy_imports") or (
        isinstance(func, ast.Attribute)
        and isinstance(func.value, ast.Name)
        and func.value.id == "lazyimports"
        and func.attr == "lazy_imports"
    )


def imports_from_tree(
    fullname: str, tree: ast.AST
) -> Generator[tuple[LazyEntity, str], None, None]:
    parts = fullname.split(".")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from ((LazyEntity.LazyImports, n.name) for n in node.names)
        elif isinstance(node, ast.ImportFrom):
            if (level := node.level) > 1:
                module = ".".join([*parts[: 1 - level], node.module])
            elif level == 1:
                module = fullname + "." + node.module
            else:
                module = node.module

            yield from (
                (LazyEntity.LazyObject, f"{module}:{n.name}") for n in node.names
            )
