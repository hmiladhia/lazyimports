import ast
from pathlib import Path


def auto_detect(path: Path):
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


def from_module_content(fullname: str, content: str):
    tree = ast.parse(content)

    for with_body in with_from_tree(tree):
        yield f"~{fullname}"
        yield from imports_from_tree(fullname, with_body)


def with_from_tree(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.With):
            if not any(is_lazy_import(item.context_expr) for item in node.items):
                continue

            yield from node.body


def is_lazy_import(node: ast.AST):
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


def imports_from_tree(fullname: str, tree: ast.AST):
    parts = fullname.split(".")

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield from (n.name for n in node.names)
        elif isinstance(node, ast.ImportFrom):
            if (level := node.level) >= 1:
                module = ".".join(parts[: 1 - level] + [node.module])
            elif level == 1:
                module = fullname + "." + node.module
            else:
                module = node.module

            yield from (f"{module}:{n.name}#2" for n in node.names)


def main():
    import argparse
    from . import LazyModules

    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    lazy_modules = LazyModules()

    lazy_modules.update(auto_detect(args.path))

    print(",".join(lazy_modules))


if __name__ == "__main__":
    main()
