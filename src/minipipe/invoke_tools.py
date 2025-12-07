"""
Invoke-based tool execution wrapper.

This module provides standardized subprocess execution using Invoke's Context.run()
instead of raw subprocess.run(). It maintains compatibility with the existing
ToolResult interface while benefiting from Invoke's standardized error handling,
logging, and configuration.

Migration Guide:
    Old approach (subprocess):
        >>> result = run_tool("pytest", {"files": "tests/"})
    
    New approach (Invoke):
        >>> from invoke import Context
        >>> ctx = Context()
        >>> result = run_tool_via_invoke("pytest", {"files": "tests/"}, ctx)
    
    Both return the same ToolResult interface for backward compatibility.

Phase G - Workstream G2 - Subprocess Migration
DOC_ID: DOC-INVOKE-TOOLS-WRAPPER-001
"""

from invoke import Context, Config
from typing import Dict, Any, Optional
from pathlib import Path
import time
from datetime import datetime, UTC

from .tools import ToolResult, get_tool_profile, render_command


def run_tool_via_invoke(
    tool_id: str,
    context: Dict[str, Any],
    invoke_ctx: Optional[Context] = None,
    timeout: Optional[int] = None,
    warn: bool = True,
    hide: bool = True,
) -> ToolResult:
    """
    Run tool using Invoke Context.run() instead of subprocess.
    
    This function wraps tool execution in Invoke's Context.run(), providing:
    - Standardized subprocess handling
    - Consistent error capturing
    - Timeout management via Invoke
    - Configuration-driven execution
    - Logging integration
    
    Args:
        tool_id: Tool identifier (e.g., "pytest", "black", "aider")
        context: Template context variables for command rendering
        invoke_ctx: Optional Invoke context (creates new if None)
        timeout: Optional timeout override (uses tool profile default if None)
        warn: If True, don't raise exceptions on non-zero exit (default: True)
        hide: If True, hide output unless there's an error (default: True)
    
    Returns:
        ToolResult with standardized output matching existing interface
    
    Example:
        >>> from invoke import Context
        >>> ctx = Context()
        >>> result = run_tool_via_invoke(
        ...     tool_id="pytest",
        ...     context={"files": "tests/unit"},
        ...     invoke_ctx=ctx
        ... )
        >>> print(f"Exit code: {result.exit_code}")
        >>> print(f"Duration: {result.duration_sec}s")
    
    Note:
        This function maintains full backward compatibility with the existing
        ToolResult interface. Calling code doesn't need to change when migrating
        from run_tool() to run_tool_via_invoke().
    """
    # Create Invoke context if not provided
    if invoke_ctx is None:
        config = Config(project_location=str(Path.cwd()))
        invoke_ctx = Context(config=config)
    
    # Get tool profile and render command
    profile = get_tool_profile(tool_id)
    cmd_parts = render_command(tool_id, context, profile)
    
    # Join command parts into a single string for Invoke
    # (Invoke expects a string, not a list)
    if isinstance(cmd_parts, list):
        cmd_str = " ".join(str(part) for part in cmd_parts)
    else:
        cmd_str = str(cmd_parts)
    
    # Determine timeout (override > profile > default)
    effective_timeout = timeout or profile.get("timeout", 300)
    
    # Track execution time
    started_at = datetime.now(UTC).isoformat()
    start_time = time.time()
    
    # Execute via Invoke
    # Note: Invoke's Result object has different attribute names than ToolResult
    try:
        result = invoke_ctx.run(
            cmd_str,
            timeout=effective_timeout,
            warn=warn,
            hide=hide,
            pty=False,  # Windows compatibility
            encoding='utf-8',  # Explicit encoding
        )
        
        completed_at = datetime.now(UTC).isoformat()
        duration_sec = time.time() - start_time
        
        # Convert Invoke Result to ToolResult
        return ToolResult(
            tool_id=tool_id,
            command_line=cmd_str,
            exit_code=result.return_code if result else -1,
            stdout=result.stdout or "" if result else "",
            stderr=result.stderr or "" if result else "",
            timed_out=False,  # Invoke raises exception on timeout
            started_at=started_at,
            completed_at=completed_at,
            duration_sec=duration_sec,
            success=(result.return_code == 0) if result else False
        )
    
    except Exception as e:
        # Handle timeouts and other errors
        completed_at = datetime.now(UTC).isoformat()
        duration_sec = time.time() - start_time
        
        # Check if it was a timeout
        is_timeout = "timeout" in str(e).lower() or duration_sec >= effective_timeout
        
        return ToolResult(
            tool_id=tool_id,
            command_line=cmd_str,
            exit_code=-1,
            stdout="",
            stderr=str(e),
            timed_out=is_timeout,
            started_at=started_at,
            completed_at=completed_at,
            duration_sec=duration_sec,
            success=False
        )


def create_invoke_context(config_overrides: Optional[Dict[str, Any]] = None) -> Context:
    """
    Create an Invoke Context with project configuration.
    
    This helper function creates a properly configured Invoke Context that:
    - Loads project-level invoke.yaml
    - Applies user-local overrides (.invoke.yaml in home dir)
    - Accepts runtime overrides
    
    Args:
        config_overrides: Optional dictionary of config overrides
    
    Returns:
        Configured Invoke Context ready for use
    
    Example:
        >>> ctx = create_invoke_context({"run": {"echo": True}})
        >>> result = run_tool_via_invoke("pytest", {}, ctx)
    """
    # Load project config
    config = Config(project_location=str(Path.cwd()))
    
    # Apply overrides if provided
    if config_overrides:
        config.update(config_overrides)
    
    return Context(config=config)


# Convenience aliases for common patterns
def run_tool_safe(tool_id: str, context: Dict[str, Any], **kwargs) -> ToolResult:
    """
    Run tool with automatic context creation (convenience wrapper).
    
    Equivalent to:
        >>> ctx = create_invoke_context()
        >>> run_tool_via_invoke(tool_id, context, ctx, **kwargs)
    
    Args:
        tool_id: Tool identifier
        context: Template context
        **kwargs: Additional arguments passed to run_tool_via_invoke
    
    Returns:
        ToolResult
    """
    ctx = create_invoke_context()
    return run_tool_via_invoke(tool_id, context, ctx, **kwargs)
