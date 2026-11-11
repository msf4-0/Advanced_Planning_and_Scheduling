"""Static boundary check: the domain package imports no infrastructure."""

import ast
from pathlib import Path

DOMAIN_DIR = Path(__file__).resolve().parents[1] / "app" / "domain"

FORBIDDEN_PREFIXES = (
    "fastapi",
    "pydantic",
    "pydantic_settings",
    "psycopg2",
    "sqlalchemy",
    "ortools",
    "api",
    "classes",
    "repository",
    "app.adapters",
    "app.config",
    "app.main",
)


def _is_forbidden(module: str) -> bool:
    return any(
        module == prefix or module.startswith(f"{prefix}.")
        for prefix in FORBIDDEN_PREFIXES
    )


def test_domain_package_has_no_infrastructure_imports():
    violations = []

    for path in sorted(DOMAIN_DIR.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                violations.extend(
                    f"{path.name}: import {alias.name}"
                    for alias in node.names
                    if _is_forbidden(alias.name)
                )
            elif (
                isinstance(node, ast.ImportFrom)
                and node.level == 0
                and node.module
                and _is_forbidden(node.module)
            ):
                violations.append(f"{path.name}: from {node.module} import ...")

    assert not violations, "Domain boundary violations:\n" + "\n".join(violations)
