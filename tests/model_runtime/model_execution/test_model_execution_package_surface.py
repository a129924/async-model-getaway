"""RED coverage for the minimal ModelExecution package and source boundary."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import async_model_gateway
import async_model_gateway as root_module
import async_model_gateway.model_runtime as model_runtime_root_module
import async_model_gateway.model_runtime.model_execution as model_execution_module
import async_model_gateway.model_runtime.model_execution.execution as execution_module
from async_model_gateway.model_runtime.model_execution import ModelExecution


def test_model_execution_package_exports_only_model_execution() -> None:
    assert model_execution_module.__all__ == ["ModelExecution"]
    assert model_execution_module.ModelExecution is ModelExecution
    assert not hasattr(model_execution_module, "RuntimeT")
    assert not hasattr(model_execution_module, "InvocationT")
    assert not hasattr(model_execution_module, "ResultT")
    assert not hasattr(model_execution_module, "invoke")


def test_existing_package_roots_do_not_reexport_model_execution() -> None:
    assert not hasattr(root_module, "ModelExecution")
    assert not hasattr(model_runtime_root_module, "ModelExecution")


def test_model_execution_has_the_locked_generic_async_signatures() -> None:
    constructor_signature = inspect.signature(ModelExecution.__init__)
    execute_signature = inspect.signature(ModelExecution.execute)

    assert tuple(parameter.__name__ for parameter in ModelExecution.__parameters__) == (
        "RuntimeT",
        "InvocationT",
        "ResultT",
    )
    assert all(
        not parameter.__covariant__ and not parameter.__contravariant__
        for parameter in ModelExecution.__parameters__
    )
    assert tuple(constructor_signature.parameters) == ("self", "invoke")
    assert constructor_signature.parameters["invoke"].kind is inspect.Parameter.KEYWORD_ONLY
    assert (
        constructor_signature.parameters["invoke"].annotation
        == "Callable[[RuntimeT, InvocationT], Awaitable[ResultT]]"
    )
    assert constructor_signature.return_annotation == "None"
    assert inspect.iscoroutinefunction(ModelExecution.execute)
    assert tuple(execute_signature.parameters) == ("self", "model", "invocation")
    assert execute_signature.parameters["model"].annotation == "LoadedRuntimeModel[RuntimeT]"
    assert execute_signature.parameters["invocation"].annotation == "InvocationT"
    assert execute_signature.return_annotation == "ResultT"


def _provider_runtime_call_paths() -> list[Path]:
    """Return every production call expression, excluding method declarations."""
    package_root = Path(async_model_gateway.__file__).parent
    call_paths: list[Path] = []

    for source_path in package_root.rglob("*.py"):
        syntax_tree = ast.parse(source_path.read_text(encoding="utf-8"))
        if any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "_provider_runtime"
            for node in ast.walk(syntax_tree)
        ):
            call_paths.append(source_path.relative_to(package_root))

    return call_paths


def test_model_execution_is_the_only_production_private_handoff_consumer() -> None:
    assert _provider_runtime_call_paths() == [
        Path("model_runtime/model_execution/execution.py"),
    ]


def test_model_execution_source_has_no_dispatch_io_or_lifecycle_dependencies() -> None:
    syntax_tree = ast.parse(inspect.getsource(execution_module))
    imported_module_roots = {
        alias.name.partition(".")[0]
        for node in ast.walk(syntax_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_from_modules = {
        node.module for node in ast.walk(syntax_tree) if isinstance(node, ast.ImportFrom)
    }
    imported_module_roots.update(
        module_name.partition(".")[0]
        for module_name in imported_from_modules
        if module_name is not None
    )
    called_attributes = {
        node.func.attr
        for node in ast.walk(syntax_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }

    assert not imported_module_roots.intersection({"asyncio", "aiofiles", "pathlib"})
    assert not any(
        module_name and ("model_artifact" in module_name or "model_pool" in module_name)
        for module_name in imported_from_modules
    )
    assert not called_attributes.intersection(
        {"create_task", "gather", "wait_for", "shield", "close", "unload"}
    )
    assert not any(isinstance(node, (ast.Try, ast.Match)) for node in ast.walk(syntax_tree))
