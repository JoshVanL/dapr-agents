"""Workflow-context injected tools.

This module defines a marker class for tools that must be invoked from within a
Dapr Workflow orchestrator.

Tools of this type accept a workflow context parameter named `ctx` and usually
return a workflow Task (e.g., the result of `ctx.call_child_workflow(...)`).

The durable agent orchestration loop detects these tools and calls them with
the current orchestrator context.

Important: AgentTool performs argument validation using `args_model` (Pydantic).
Since MCP-derived schemas do not include the `ctx` parameter, we preserve `ctx`
across validation and re-inject it before calling the underlying function.
"""

from __future__ import annotations

from typing import Any, Callable, Dict

from dapr_agents.tool.base import AgentTool


class WorkflowContextInjectedTool(AgentTool):
    """AgentTool that must be invoked from inside a workflow orchestrator.

    The function signature is expected to include `ctx`. Because `args_model`
    typically validates only MCP tool arguments (and would drop `ctx`), this
    subclass preserves `ctx` while still validating the MCP arguments.
    """

    def _validate_and_prepare_args(
        self, func: Callable, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        ctx = kwargs.pop("ctx", None)
        prepared = super()._validate_and_prepare_args(func, *args, **kwargs)
        if ctx is not None:
            prepared["ctx"] = ctx
        return prepared
