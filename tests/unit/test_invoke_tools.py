"""
Tests for Invoke-based tool execution wrapper.

Phase G - Workstream G2 - Subprocess Migration Tests
DOC_ID: DOC-INVOKE-TOOLS-TESTS-001
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from invoke import Context, Result

from src.minipipe.invoke_tools import (
    run_tool_via_invoke,
    create_invoke_context,
    run_tool_safe,
)
from src.minipipe.tools import ToolResult


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_context():
    """Create a mock Invoke Context."""
    ctx = Mock(spec=Context)
    return ctx


@pytest.fixture
def mock_tool_profile():
    """Mock tool profile data."""
    return {
        "binary": "pytest",
        "timeout": 60,
        "flags": ["-v"],
    }


@pytest.fixture
def mock_successful_result():
    """Mock successful Invoke Result."""
    result = Mock(spec=Result)
    result.return_code = 0
    result.stdout = "Test output"
    result.stderr = ""
    result.ok = True
    return result


@pytest.fixture
def mock_failed_result():
    """Mock failed Invoke Result."""
    result = Mock(spec=Result)
    result.return_code = 1
    result.stdout = ""
    result.stderr = "Test error"
    result.ok = False
    return result


# ============================================================================
# Basic Functionality Tests
# ============================================================================

def test_run_tool_via_invoke_success(mock_context, mock_tool_profile, mock_successful_result):
    """Test successful tool execution via Invoke."""
    # Setup
    mock_context.run.return_value = mock_successful_result
    
    with patch('src.minipipe.invoke_tools.get_tool_profile', return_value=mock_tool_profile):
        with patch('src.minipipe.invoke_tools.render_command', return_value=["pytest", "-v", "tests/"]):
            # Execute
            result = run_tool_via_invoke(
                tool_id="pytest",
                context={"files": "tests/"},
                invoke_ctx=mock_context
            )
    
    # Verify
    assert isinstance(result, ToolResult)
    assert result.success is True
    assert result.exit_code == 0
    assert result.stdout == "Test output"
    assert result.stderr == ""
    assert result.timed_out is False
    assert result.tool_id == "pytest"
    
    # Verify Invoke was called correctly
    mock_context.run.assert_called_once()
    call_args = mock_context.run.call_args
    assert "pytest -v tests/" in call_args[0][0]
    assert call_args[1]["warn"] is True
    assert call_args[1]["hide"] is True
    assert call_args[1]["pty"] is False


def test_run_tool_via_invoke_failure(mock_context, mock_tool_profile, mock_failed_result):
    """Test failed tool execution via Invoke."""
    # Setup
    mock_context.run.return_value = mock_failed_result
    
    with patch('src.minipipe.invoke_tools.get_tool_profile', return_value=mock_tool_profile):
        with patch('src.minipipe.invoke_tools.render_command', return_value=["pytest", "tests/"]):
            # Execute
            result = run_tool_via_invoke(
                tool_id="pytest",
                context={"files": "tests/"},
                invoke_ctx=mock_context
            )
    
    # Verify
    assert isinstance(result, ToolResult)
    assert result.success is False
    assert result.exit_code == 1
    assert result.stdout == ""
    assert result.stderr == "Test error"
    assert result.timed_out is False


def test_run_tool_via_invoke_timeout(mock_context, mock_tool_profile):
    """Test tool execution timeout handling."""
    # Setup - simulate timeout exception
    mock_context.run.side_effect = Exception("timeout exceeded")
    
    with patch('src.minipipe.invoke_tools.get_tool_profile', return_value=mock_tool_profile):
        with patch('src.minipipe.invoke_tools.render_command', return_value=["pytest", "tests/"]):
            # Execute
            result = run_tool_via_invoke(
                tool_id="pytest",
                context={"files": "tests/"},
                invoke_ctx=mock_context,
                timeout=1  # Override timeout
            )
    
    # Verify
    assert isinstance(result, ToolResult)
    assert result.success is False
    assert result.exit_code == -1
    assert result.timed_out is True
    assert "timeout" in result.stderr.lower()


def test_run_tool_via_invoke_custom_timeout(mock_context, mock_tool_profile, mock_successful_result):
    """Test custom timeout override."""
    # Setup
    mock_context.run.return_value = mock_successful_result
    
    with patch('src.minipipe.invoke_tools.get_tool_profile', return_value=mock_tool_profile):
        with patch('src.minipipe.invoke_tools.render_command', return_value=["pytest"]):
            # Execute with custom timeout
            result = run_tool_via_invoke(
                tool_id="pytest",
                context={},
                invoke_ctx=mock_context,
                timeout=120  # Custom timeout
            )
    
    # Verify timeout was used
    call_args = mock_context.run.call_args
    assert call_args[1]["timeout"] == 120


# ============================================================================
# Context Creation Tests
# ============================================================================

def test_create_invoke_context_basic():
    """Test basic Invoke Context creation."""
    ctx = create_invoke_context()
    
    assert isinstance(ctx, Context)
    assert ctx.config is not None


def test_create_invoke_context_with_overrides():
    """Test Invoke Context creation with config overrides."""
    overrides = {
        "run": {"echo": True},
    }
    
    ctx = create_invoke_context(config_overrides=overrides)
    
    assert isinstance(ctx, Context)
    # Note: config.update() may not work as expected in all Invoke versions
    # This test verifies the function doesn't crash with overrides


# ============================================================================
# Convenience Function Tests
# ============================================================================

def test_run_tool_safe(mock_tool_profile, mock_successful_result):
    """Test run_tool_safe convenience function."""
    with patch('src.minipipe.invoke_tools.get_tool_profile', return_value=mock_tool_profile):
        with patch('src.minipipe.invoke_tools.render_command', return_value=["echo", "test"]):
            with patch('src.minipipe.invoke_tools.Context') as MockContext:
                mock_ctx = Mock()
                mock_ctx.run.return_value = mock_successful_result
                MockContext.return_value = mock_ctx
                
                result = run_tool_safe("echo", {"message": "test"})
                
                assert isinstance(result, ToolResult)
                assert result.success is True


# ============================================================================
# Command Rendering Tests
# ============================================================================

def test_command_list_to_string(mock_context, mock_tool_profile, mock_successful_result):
    """Test that command list is properly joined into string."""
    mock_context.run.return_value = mock_successful_result
    
    with patch('src.minipipe.invoke_tools.get_tool_profile', return_value=mock_tool_profile):
        with patch('src.minipipe.invoke_tools.render_command', return_value=["pytest", "-v", "--cov", "tests/"]):
            result = run_tool_via_invoke(
                tool_id="pytest",
                context={},
                invoke_ctx=mock_context
            )
    
    # Verify command was joined with spaces
    call_args = mock_context.run.call_args
    assert call_args[0][0] == "pytest -v --cov tests/"


def test_command_string_passed_through(mock_context, mock_tool_profile, mock_successful_result):
    """Test that command string is passed through as-is."""
    mock_context.run.return_value = mock_successful_result
    
    with patch('src.minipipe.invoke_tools.get_tool_profile', return_value=mock_tool_profile):
        with patch('src.minipipe.invoke_tools.render_command', return_value="pytest -v"):
            result = run_tool_via_invoke(
                tool_id="pytest",
                context={},
                invoke_ctx=mock_context
            )
    
    # Verify command was used as-is
    call_args = mock_context.run.call_args
    assert call_args[0][0] == "pytest -v"


# ============================================================================
# Error Handling Tests
# ============================================================================

def test_run_tool_via_invoke_exception_handling(mock_context, mock_tool_profile):
    """Test that exceptions are caught and returned as ToolResult."""
    # Setup - simulate exception
    mock_context.run.side_effect = RuntimeError("Unexpected error")
    
    with patch('src.minipipe.invoke_tools.get_tool_profile', return_value=mock_tool_profile):
        with patch('src.minipipe.invoke_tools.render_command', return_value=["pytest"]):
            result = run_tool_via_invoke(
                tool_id="pytest",
                context={},
                invoke_ctx=mock_context
            )
    
    # Verify error is captured in ToolResult
    assert isinstance(result, ToolResult)
    assert result.success is False
    assert result.exit_code == -1
    assert "Unexpected error" in result.stderr


# ============================================================================
# Integration Tests (TODO-016 MockContext)
# ============================================================================

class MockContext(Context):
    """
    Mock Invoke Context for testing without actual subprocess execution.
    
    Simulates Context.run() behavior for unit tests.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands_run = []
        self.mock_results = {}
    
    def set_mock_result(self, command_pattern: str, result: Result):
        """Configure mock result for a command pattern."""
        self.mock_results[command_pattern] = result
    
    def run(self, command, **kwargs):
        """Mock run implementation that returns configured results."""
        self.commands_run.append((command, kwargs))
        
        # Find matching mock result
        for pattern, result in self.mock_results.items():
            if pattern in command:
                return result
        
        # Default successful result
        result = Mock(spec=Result)
        result.return_code = 0
        result.stdout = f"Mocked output for: {command}"
        result.stderr = ""
        result.ok = True
        return result


def test_mock_context_basic():
    """Test MockContext basic functionality."""
    ctx = MockContext()
    
    # Run a command
    result = ctx.run("echo test")
    
    # Verify it was tracked
    assert len(ctx.commands_run) == 1
    assert ctx.commands_run[0][0] == "echo test"
    assert result.return_code == 0


def test_mock_context_with_custom_result():
    """Test MockContext with custom result."""
    ctx = MockContext()
    
    # Configure mock result
    custom_result = Mock(spec=Result)
    custom_result.return_code = 1
    custom_result.stdout = ""
    custom_result.stderr = "Custom error"
    
    ctx.set_mock_result("pytest", custom_result)
    
    # Run command
    result = ctx.run("pytest tests/")
    
    # Verify custom result was returned
    assert result.return_code == 1
    assert result.stderr == "Custom error"


def test_run_tool_via_invoke_with_mock_context(mock_tool_profile):
    """Test full integration with MockContext."""
    ctx = MockContext()
    
    # Configure successful result
    success_result = Mock(spec=Result)
    success_result.return_code = 0
    success_result.stdout = "All tests passed"
    success_result.stderr = ""
    
    ctx.set_mock_result("pytest", success_result)
    
    with patch('src.minipipe.invoke_tools.get_tool_profile', return_value=mock_tool_profile):
        with patch('src.minipipe.invoke_tools.render_command', return_value=["pytest", "tests/"]):
            result = run_tool_via_invoke(
                tool_id="pytest",
                context={},
                invoke_ctx=ctx
            )
    
    # Verify result
    assert result.success is True
    assert result.stdout == "All tests passed"
    assert len(ctx.commands_run) == 1


# ============================================================================
# Backward Compatibility Tests
# ============================================================================

def test_tool_result_interface_compatibility(mock_context, mock_tool_profile, mock_successful_result):
    """Test that ToolResult interface is maintained for backward compatibility."""
    mock_context.run.return_value = mock_successful_result
    
    with patch('src.minipipe.invoke_tools.get_tool_profile', return_value=mock_tool_profile):
        with patch('src.minipipe.invoke_tools.render_command', return_value=["pytest"]):
            result = run_tool_via_invoke(
                tool_id="pytest",
                context={},
                invoke_ctx=mock_context
            )
    
    # Verify all expected ToolResult attributes exist
    assert hasattr(result, 'tool_id')
    assert hasattr(result, 'command_line')
    assert hasattr(result, 'exit_code')
    assert hasattr(result, 'stdout')
    assert hasattr(result, 'stderr')
    assert hasattr(result, 'timed_out')
    assert hasattr(result, 'started_at')
    assert hasattr(result, 'completed_at')
    assert hasattr(result, 'duration_sec')
    assert hasattr(result, 'success')
    
    # Verify to_dict() method works
    result_dict = result.to_dict()
    assert isinstance(result_dict, dict)
    assert 'tool_id' in result_dict
    assert 'exit_code' in result_dict
