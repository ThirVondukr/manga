import pkgutil
from collections.abc import Sequence

import pytest
from pytest_archon import archrule

from app import adapters


def test_core_cant_import_adapters() -> None:
    (
        archrule("core_imports")
        .match("app.core.**")
        .should_not_import("app.adapters.*")
        .check("app.core")
    )


def test_adapters_dont_import_services_or_repositories() -> None:
    (
        archrule("adapters_dont_import_services")
        .match("app.adapters.*")
        .should_not_import(
            "app.core.*.repositories",
            "app.core.*.services",
        )
        .check("app.adapters")
    )


def test_adapters_dont_import_each_other() -> None:
    adapter_modules = (
        module.name for module in pkgutil.iter_modules(adapters.__path__)
    )
    exclude = {"api": ["graphql.app"]}
    for adapter in adapter_modules:
        rule = (
            archrule(f"adapter_{adapter}")
            .match("app.adapters.*")
            .should_not_import("app.adapters.*")
            .may_import(f"app.adapters.{adapter}.*")
        )
        for may_import in exclude.get(adapter, []):
            rule = rule.may_import(f"app.adapters.{may_import}")

        rule.check(f"app.adapters.{adapter}")


@pytest.mark.parametrize(
    ("modules", "libraries"),
    [
        (
            ["app.core", "lib"],
            ["fastapi", "strawberry", "asyncpg", "starlette", "uvicorn"],
        ),
    ],
)
def test_banned_libraries(
    modules: str | list[str],
    libraries: Sequence[str],
) -> None:
    if isinstance(modules, str):
        modules = [modules]

    for module in modules:
        (
            archrule(f"{module}-banned-libs")
            .match(f"{module}.*")
            .should_not_import(*libraries)
            .check(module)
        )
