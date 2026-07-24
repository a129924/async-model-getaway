"""RED coverage for the internal executor source and package boundary."""

from __future__ import annotations

import ast
import inspect

import async_model_gateway as root_module
import async_model_gateway.model_runtime as model_runtime_root_module
import async_model_gateway.model_runtime.model_execution as model_execution_module
import async_model_gateway.model_runtime.model_execution.execution as execution_module


def test_model_execution_package_reexports_no_executor_types() -> None:
    assert model_execution_module.__all__ == []
    assert not hasattr(model_execution_module, "ModelExecution")
    assert not hasattr(model_execution_module, "ModelExecutor")


def test_package_roots_do_not_reexport_internal_executor_types() -> None:
    assert not hasattr(root_module, "ModelExecution")
    assert not hasattr(model_runtime_root_module, "ModelExecutor")


def test_executor_source_has_no_binding_owner_or_late_dispatch() -> None:
    syntax_tree = ast.parse(inspect.getsource(execution_module))
    imported_from_modules = {
        node.module for node in ast.walk(syntax_tree) if isinstance(node, ast.ImportFrom)
    }
    imported_module_roots = {
        alias.name.partition(".")[0]
        for node in ast.walk(syntax_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    called_attributes = {
        node.func.attr
        for node in ast.walk(syntax_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }

    assert not any(
        module_name
        and any(
            forbidden in module_name
            for forbidden in ("model_pool", "model_artifact", "runtime_binding", "composition")
        )
        for module_name in imported_from_modules
    )
    assert "asyncio" in imported_module_roots
    assert not called_attributes.intersection({"resolve", "load", "get_or_load"})
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "isinstance"
        for node in ast.walk(syntax_tree)
    )
    assert not any(
        isinstance(node, ast.Attribute) and node.attr == "loader_family"
        for node in ast.walk(syntax_tree)
    )
