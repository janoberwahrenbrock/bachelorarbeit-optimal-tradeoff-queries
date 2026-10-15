"""Keep the domain, computation, orchestration and analysis boundaries explicit."""
import ast
from pathlib import Path


def runtime_nodes(node):
    yield node
    if isinstance(node, ast.If) and (
        isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING"
        or isinstance(node.test, ast.Attribute) and node.test.attr == "TYPE_CHECKING"
    ):
        for child in node.orelse:
            yield from runtime_nodes(child)
        return
    for child in ast.iter_child_nodes(node):
        yield from runtime_nodes(child)


def imports():
    root = Path(__file__).parents[2] / "src" / "otqa"
    modules = {}
    for path in root.rglob("*.py"):
        parts = path.relative_to(root.parent).with_suffix("").parts
        module = ".".join(parts[:-1] if parts[-1] == "__init__" else parts)
        modules[module] = path
    edges = {name: set() for name in modules}
    all_imports = {name: set() for name in modules}
    for module, path in modules.items():
        package = module if path.name == "__init__.py" else module.rsplit(".", 1)[0]
        tree = ast.parse(path.read_text())
        runtime = {id(node) for node in runtime_nodes(tree)}
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                prefix = ".".join(package.split(".")[:len(package.split(".")) - node.level + 1]) if node.level else ""
                target = ".".join(part for part in (prefix, node.module) if part)
                names = [target] + [target + "." + alias.name for alias in node.names]
            all_imports[module].update(names)
            if id(node) in runtime:
                edges[module].update(name for name in names if name in modules and name != module)
    return all_imports, edges


def test_internal_dependency_graph_has_no_cycles():
    _, graph = imports()
    visited, active = set(), []
    def visit(module):
        assert module not in active, " -> ".join([*active, module])
        if module in visited:
            return
        active.append(module)
        for dependency in sorted(graph[module]):
            visit(dependency)
        active.pop()
        visited.add(module)
    for module in sorted(graph):
        visit(module)


def test_computation_and_domain_do_not_depend_on_orchestration_or_legacy():
    graph, _ = imports()
    for module, dependencies in graph.items():
        for dependency in dependencies:
            assert dependency.split(".")[0] not in ("multistep", "onestep"), (module, dependency)
            if module.startswith(("otqa.models", "otqa.numerics", "otqa.geometry", "otqa.state", "otqa.queries", "otqa.planning")):
                assert not dependency.startswith(("otqa.runtime", "otqa.application", "otqa.experiments", "otqa.analysis", "otqa.cli")), (module, dependency)
            if module.startswith("otqa.analysis"):
                assert not dependency.startswith(("otqa.experiments", "otqa.runtime.supervisor", "otqa.runtime.case", "otqa.application.")), (module, dependency)
