"""Layering policy: what the package may import, own, and write.

The package implements the FMI half of a SysML dialect; the dialect itself is a
dependency, never a sibling. The package is split into a shared ``core`` and one
self-contained subpackage per artifact family. These tests hold that boundary
recursively: core imports no family, a family imports no sibling, only the
facade and the CLI collect families, every family directory is registered, and
every module is reachable.
"""

from __future__ import annotations

import ast
import re
import sys
from collections.abc import Collection
from pathlib import Path

import pytest

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # Python 3.10 runtime without tomllib
    import tomli as tomllib

pytestmark = pytest.mark.static

PACKAGE = "pyfmi_interfaces"

REPO_ROOT = Path(__file__).resolve().parent.parent

SRC_ROOT = REPO_ROOT / "src"

PACKAGE_ROOT = SRC_ROOT / PACKAGE

PYPROJECT = REPO_ROOT / "pyproject.toml"

FACADE = PACKAGE_ROOT / "__init__.py"

CLI = PACKAGE_ROOT / "cli.py"

#: The sibling artifact library is a wheel dependency, never a package this one
#: imports.
FORBIDDEN_IMPORT = "pyssp_sysml2"

#: The SysML parser moved to ``pyfmi_sysml``; this package is parser-free, so no
#: module may import it at all (not even under ``TYPE_CHECKING``).
SYSML_PARSER = "pycps_sysml2"

#: The only third party ``core`` may import: the FMI XML library whose document
#: model and serializer this package maps onto.
ALLOWED_CORE_THIRD_PARTY = frozenset({"pyssp_standard"})

#: Directories under the package that are not artifact families.
NON_FAMILY_DIRECTORIES = frozenset({"core", "fmi2_headers"})

#: Runtime dependencies are immutable release assets, pinned by direct URL.
DIRECT_URL = re.compile(r"^[A-Za-z0-9_.-]+ @ https://\S+$")

EXPECTED_PYTHON = ">=3.11"

#: The documented public surface of the facade, exactly.
EXPECTED_PUBLIC = frozenset(
    {
        "Component",
        "Experiment",
        "ExportIdentity",
        "Reduction",
        "Variable",
        "__version__",
        "fmi2_headers",
        "generate_c_headers",
        "generate_c_runtime",
        "generate_model_description",
        "generate_modelica",
    }
)


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _dotted_name(path: Path) -> str:
    """The import name of ``path``, without ``__init__`` for a package."""
    parts = list(path.relative_to(SRC_ROOT).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _modules() -> list[tuple[Path, str, ast.Module]]:
    """Every module in the package: path, dotted name, parsed tree."""
    return [
        (path, _dotted_name(path), _tree(path))
        for path in sorted(PACKAGE_ROOT.rglob("*.py"))
    ]


def _location(path: Path, lineno: int) -> str:
    return f"{path.relative_to(REPO_ROOT).as_posix()}:{lineno}"


def _package_of(module: str, path: Path) -> str:
    """The package a module's relative imports resolve against."""
    return module if path.name == "__init__.py" else module.rpartition(".")[0]


def _from_target(package: str, node: ast.ImportFrom) -> str:
    """The absolute module named by an ``ImportFrom`` node."""
    if not node.level:
        return node.module or ""
    base = package.split(".")
    if node.level > 1:
        base = base[: -(node.level - 1)]
    return ".".join(base + ([node.module] if node.module else []))


def _imports(
    module: str,
    path: Path,
    tree: ast.Module,
    known: Collection[str] = (),
) -> list[tuple[str, int]]:
    """Absolute import targets of one module, with their line numbers."""
    package = _package_of(module, path)
    targets: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            targets.extend((alias.name, node.lineno) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            name = _from_target(package, node)
            if not name:
                continue
            targets.append((name, node.lineno))
            for alias in node.names:
                candidate = f"{name}.{alias.name}"
                if candidate in known:
                    targets.append((candidate, node.lineno))
    return targets


def _family_names() -> list[str]:
    """Artifact-family subpackages: package directories other than ``core``."""
    return sorted(
        path.name
        for path in PACKAGE_ROOT.iterdir()
        if path.is_dir()
        and (path / "__init__.py").is_file()
        and path.name not in NON_FAMILY_DIRECTORIES
    )


def _pyproject() -> dict:
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def _entry_points() -> set[str]:
    """Modules named as console-script targets; they are graph roots."""
    scripts = _pyproject().get("project", {}).get("scripts", {})
    roots = set()
    for target in scripts.values():
        module = target.split(":")[0]
        if module.split(".")[0] == PACKAGE:
            roots.add(module)
    return roots


def _exports(tree: ast.Module) -> tuple[object, ast.stmt] | None:
    """The literal ``__all__`` value and its assignment node, if present."""
    for node in tree.body:
        value = None
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        ):
            value = node.value
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
        ):
            value = node.value
        if value is not None:
            return ast.literal_eval(value), node
    return None


def _all_mutations(tree: ast.Module, assignment: ast.stmt) -> list[int]:
    """Lines that rebind or mutate ``__all__`` after its literal assignment."""
    lines = set()
    for node in ast.walk(tree):
        if node is assignment:
            continue
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = node.targets
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
            targets = [node.target]
        for target in targets:
            for name in ast.walk(target):
                if isinstance(name, ast.Name) and name.id == "__all__":
                    lines.add(node.lineno)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            value = node.func.value
            if isinstance(value, ast.Name) and value.id == "__all__":
                lines.add(node.lineno)
    return sorted(lines)


def _module_bindings(
    module: str,
    path: Path,
    tree: ast.Module,
    known: Collection[str],
) -> set[str]:
    """Names this module binds to module objects rather than to symbols."""
    package = _package_of(module, path)
    bindings: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            bindings.update(
                alias.asname or alias.name.split(".")[0] for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            name = _from_target(package, node)
            for alias in node.names:
                if alias.name != "*" and f"{name}.{alias.name}" in known:
                    bindings.add(alias.asname or alias.name)
    return bindings


def test_sources_do_not_import_the_dialect_package():
    offenders = [
        _location(path, lineno)
        for path, module, tree in _modules()
        for name, lineno in _imports(module, path, tree)
        if name.split(".")[0] == FORBIDDEN_IMPORT
    ]
    assert not offenders, (
        f"{FORBIDDEN_IMPORT} is a dependency, not a package this one imports: "
        f"{offenders}"
    )


def _runtime_imports(
    module: str, path: Path, tree: ast.Module
) -> list[tuple[str, int]]:
    """Absolute import targets outside an ``if TYPE_CHECKING:`` block."""
    package = _package_of(module, path)
    targets: list[tuple[str, int]] = []

    def visit(node: ast.AST) -> None:
        if isinstance(node, ast.If) and _is_type_checking(node.test):
            return
        if isinstance(node, ast.Import):
            targets.extend((alias.name, node.lineno) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            name = _from_target(package, node)
            if name:
                targets.append((name, node.lineno))
        for child in ast.iter_child_nodes(node):
            visit(child)

    visit(tree)
    return targets


def _is_type_checking(test: ast.expr) -> bool:
    if isinstance(test, ast.Name):
        return test.id == "TYPE_CHECKING"
    return isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"


def test_sources_import_no_sysml_parser():
    """``pyfmi_interfaces`` is parser-free; ``pyfmi_sysml`` owns ingestion.

    The check walks every import, including ``TYPE_CHECKING`` blocks, so an
    annotation alone cannot pull the parser back in.
    """
    offenders = [
        _location(path, lineno)
        for path, module, tree in _modules()
        for name, lineno in _imports(module, path, tree)
        if name.split(".")[0] == SYSML_PARSER
    ]
    assert not offenders, (
        f"{SYSML_PARSER} is owned by pyfmi_sysml; no module here may import it: "
        f"{offenders}"
    )


def test_core_imports_only_the_dialect_fmi_and_itself():
    core = f"{PACKAGE}.core"
    offenders = []
    for path, module, tree in _modules():
        if module != core and not module.startswith(f"{core}."):
            continue
        for name, lineno in _imports(module, path, tree):
            top = name.split(".")[0]
            if top != PACKAGE:
                if top in sys.stdlib_module_names or top in ALLOWED_CORE_THIRD_PARTY:
                    continue
                offenders.append(f"{_location(path, lineno)} imports {name}")
            elif name != core and not name.startswith(f"{core}."):
                offenders.append(f"{_location(path, lineno)} imports {name}")
    assert not offenders, (
        "core imports only stdlib, pyssp_standard, and "
        f"pyfmi_interfaces.core.*: {offenders}"
    )


def test_a_family_imports_only_itself_and_core():
    families = set(_family_names())
    offenders = []
    for path, module, tree in _modules():
        parts = module.split(".")
        if len(parts) < 2 or parts[1] not in families:
            continue
        family = parts[1]
        for name, lineno in _imports(module, path, tree):
            target = name.split(".")
            if name == PACKAGE:
                offenders.append(
                    f"{_location(path, lineno)}: {family} imports the facade"
                )
            elif (
                target[0] == PACKAGE
                and len(target) > 1
                and target[1] in families
                and target[1] != family
            ):
                offenders.append(
                    f"{_location(path, lineno)}: {family} imports {target[1]}"
                )
    assert not offenders, (
        "an artifact family must not import a sibling family; only its own "
        f"modules and pyfmi_interfaces.core.* are allowed: {offenders}"
    )


def test_family_packages_are_collected_only_at_the_top():
    families = set(_family_names())
    roots = {FACADE, CLI}
    offenders = []
    for path, module, tree in _modules():
        if path in roots:
            continue
        parts = module.split(".")
        owner = parts[1] if len(parts) > 1 and parts[1] in families else None
        for name, lineno in _imports(module, path, tree):
            target = name.split(".")
            if (
                target[0] == PACKAGE
                and len(target) > 1
                and target[1] in families
                and target[1] != owner
            ):
                offenders.append(
                    f"{_location(path, lineno)} imports family {target[1]}"
                )
    assert not offenders, (
        "only pyfmi_interfaces/__init__.py and pyfmi_interfaces/cli.py may collect "
        f"artifact families: {offenders}"
    )


def test_cli_registers_only_the_packaging_family():
    """Source-taking commands moved to ``pyfmi-sysml``; ``package`` stays here."""
    registered = set()
    for node in ast.walk(_tree(CLI)):
        if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            parts = node.module.split(".")
            if (
                parts[0] == PACKAGE
                and len(parts) > 1
                and any(alias.name == "COMMANDS" for alias in node.names)
            ):
                registered.add(parts[1])
    assert registered == {"fmu"}, (
        "cli.py must register only the packaging family; the source-taking "
        f"families register in pyfmi_sysml: registered={sorted(registered)}"
    )


def test_every_module_is_reachable_from_a_root():
    parsed = {module: (path, tree) for path, module, tree in _modules()}
    roots = {PACKAGE} | _entry_points()
    missing_roots = sorted(roots - parsed.keys())
    assert not missing_roots, f"declared roots with no module: {missing_roots}"

    seen = set(roots)
    queue = list(roots)
    while queue:
        current = queue.pop()
        path, tree = parsed[current]
        for imported, _lineno in _imports(current, path, tree, known=parsed.keys()):
            if imported in parsed and imported not in seen:
                seen.add(imported)
                queue.append(imported)

    orphans = sorted(
        module
        for module, (path, _tree_) in parsed.items()
        if path.name != "__init__.py" and module not in seen
    )
    assert not orphans, (
        "modules no root reaches; import them from a package __init__ or delete "
        f"them: {orphans}"
    )


def test_runtime_dependency_is_one_pinned_direct_url():
    project = _pyproject()["project"]
    dependencies = project.get("dependencies", [])
    assert len(dependencies) == 1, (
        f"exactly one runtime dependency expected, found {dependencies}"
    )
    wrong = [dep for dep in dependencies if not DIRECT_URL.match(dep)]
    assert not wrong, f"runtime dependencies are not direct wheel URLs: {wrong}"
    dialect = [
        dep
        for dep in dependencies
        if FORBIDDEN_IMPORT in dep or SYSML_PARSER in dep
    ]
    assert not dialect, f"no SysML parser may be a runtime dependency: {dialect}"


def test_python_floor_matches_pyproject():
    requires = _pyproject()["project"].get("requires-python")
    assert requires == EXPECTED_PYTHON, (
        f"pyproject.toml requires-python must stay {EXPECTED_PYTHON!r}, "
        f"found {requires!r}"
    )


def test_every_module_has_a_docstring():
    missing = [
        _dotted_name(path)
        for path, _module, tree in _modules()
        if not ast.get_docstring(tree)
    ]
    assert not missing, f"modules without a docstring: {missing}"


def test_generation_writes_only_where_the_caller_says():
    """No module may derive an output path from its own location."""
    offenders = []
    for path, _module, _tree_ in _modules():
        text = path.read_text(encoding="utf-8")
        for number, line in enumerate(text.splitlines(), start=1):
            for pattern in ("__file__", "getcwd(", "os.getcwd"):
                if pattern in line:
                    offenders.append(f"{_location(path, number)}: {pattern}")
    assert not offenders, (
        "output paths must come from an explicit argument, not from the process: "
        f"{offenders}"
    )


def test_public_facade_exports_the_documented_symbols():
    path, module, tree = next(entry for entry in _modules() if entry[0] == FACADE)
    found = _exports(tree)
    assert found is not None, f"{path.relative_to(REPO_ROOT).as_posix()}: no __all__"
    exported, node = found
    mutated = _all_mutations(tree, node)
    assert not mutated, (
        f"{_location(path, mutated[0])}: __all__ must be one literal assignment, "
        "not mutated at runtime"
    )
    names = list(exported)
    missing = sorted(EXPECTED_PUBLIC - set(names))
    unexpected = sorted(set(names) - EXPECTED_PUBLIC)
    assert set(names) == EXPECTED_PUBLIC and len(names) == len(set(names)), (
        f"{_location(path, node.lineno)}: __all__ must equal the documented "
        f"facade; missing={missing} unexpected={unexpected}"
    )
    known = {dotted for _path, dotted, _tree_ in _modules()}
    modules_exported = sorted(
        _module_bindings(module, path, tree, known) & set(names)
    )
    assert not modules_exported, (
        f"{_location(path, node.lineno)}: __all__ must export symbols, not "
        f"module objects: {modules_exported}"
    )
