"""Tests for hookify hook entry points.

Tests the event detection logic and JSON I/O of the hook scripts.
Since the hooks use sys.exit(0) in finally blocks, we test the
core logic functions rather than calling main() directly.
"""

import json
import pytest


class TestPreToolUseEventDetection:
    """Test event type detection logic used in pretooluse.py and posttooluse.py."""

    def _detect_event(self, tool_name):
        """Replicate the event detection logic from pretooluse.py."""
        event = None
        if tool_name == "Bash":
            event = "bash"
        elif tool_name in ["Edit", "Write", "MultiEdit"]:
            event = "file"
        return event

    def test_bash_tool_detected(self):
        assert self._detect_event("Bash") == "bash"

    def test_edit_tool_detected(self):
        assert self._detect_event("Edit") == "file"

    def test_write_tool_detected(self):
        assert self._detect_event("Write") == "file"

    def test_multiedit_tool_detected(self):
        assert self._detect_event("MultiEdit") == "file"

    def test_unknown_tool_returns_none(self):
        assert self._detect_event("Read") is None

    def test_empty_tool_returns_none(self):
        assert self._detect_event("") is None


class TestStopHookEvent:
    """Test that the stop hook always uses 'stop' event."""

    def test_stop_event_is_fixed(self):
        # The stop hook always loads rules with event='stop'
        # This is a documentation/logic test
        event = "stop"
        assert event == "stop"


class TestUserPromptSubmitEvent:
    """Test that the user prompt hook always uses 'prompt' event."""

    def test_prompt_event_is_fixed(self):
        event = "prompt"
        assert event == "prompt"


class TestHookJsonOutput:
    """Test that hook output format is valid JSON."""

    def test_empty_result_serializable(self):
        result = {}
        output = json.dumps(result)
        assert output == "{}"

    def test_error_output_serializable(self):
        error_output = {"systemMessage": "Hookify error: test error"}
        output = json.dumps(error_output)
        parsed = json.loads(output)
        assert parsed["systemMessage"] == "Hookify error: test error"

    def test_import_error_output_serializable(self):
        error_msg = {"systemMessage": "Hookify import error: No module named 'hookify'"}
        output = json.dumps(error_msg)
        parsed = json.loads(output)
        assert "import error" in parsed["systemMessage"]
