"""Tests for hookify rule engine."""

import pytest
from hookify.core.config_loader import Rule, Condition
from hookify.core.rule_engine import RuleEngine, compile_regex


# --- Fixtures ---

@pytest.fixture
def engine():
    return RuleEngine()


def make_rule(name="test-rule", conditions=None, action="warn", tool_matcher=None, message="Test warning"):
    """Helper to create a Rule with defaults."""
    return Rule(
        name=name,
        enabled=True,
        event="bash",
        conditions=conditions or [],
        action=action,
        tool_matcher=tool_matcher,
        message=message,
    )


def make_condition(field="command", operator="regex_match", pattern="rm\\s+-rf"):
    return Condition(field=field, operator=operator, pattern=pattern)


# --- compile_regex ---

class TestCompileRegex:
    def test_compiles_valid_pattern(self):
        regex = compile_regex(r"rm\s+-rf")
        assert regex.search("rm -rf /tmp")

    def test_case_insensitive(self):
        regex = compile_regex(r"DELETE")
        assert regex.search("delete from table")

    def test_caching_returns_same_object(self):
        r1 = compile_regex(r"test_pattern_xyz")
        r2 = compile_regex(r"test_pattern_xyz")
        assert r1 is r2


# --- _matches_tool ---

class TestMatchesTool:
    def test_wildcard_matches_any(self, engine):
        assert engine._matches_tool("*", "Bash") is True
        assert engine._matches_tool("*", "Edit") is True

    def test_exact_match(self, engine):
        assert engine._matches_tool("Bash", "Bash") is True
        assert engine._matches_tool("Bash", "Edit") is False

    def test_pipe_separated_or(self, engine):
        assert engine._matches_tool("Edit|Write", "Edit") is True
        assert engine._matches_tool("Edit|Write", "Write") is True
        assert engine._matches_tool("Edit|Write", "Bash") is False


# --- _check_condition ---

class TestCheckCondition:
    def test_regex_match(self, engine):
        cond = make_condition(operator="regex_match", pattern=r"rm\s+-rf")
        assert engine._check_condition(cond, "Bash", {"command": "rm -rf /tmp"}) is True
        assert engine._check_condition(cond, "Bash", {"command": "ls -la"}) is False

    def test_contains(self, engine):
        cond = make_condition(operator="contains", pattern="sudo")
        assert engine._check_condition(cond, "Bash", {"command": "sudo rm file"}) is True
        assert engine._check_condition(cond, "Bash", {"command": "rm file"}) is False

    def test_equals(self, engine):
        cond = make_condition(field="command", operator="equals", pattern="ls")
        assert engine._check_condition(cond, "Bash", {"command": "ls"}) is True
        assert engine._check_condition(cond, "Bash", {"command": "ls -la"}) is False

    def test_not_contains(self, engine):
        cond = make_condition(operator="not_contains", pattern="--dry-run")
        assert engine._check_condition(cond, "Bash", {"command": "deploy"}) is True
        assert engine._check_condition(cond, "Bash", {"command": "deploy --dry-run"}) is False

    def test_starts_with(self, engine):
        cond = make_condition(operator="starts_with", pattern="sudo")
        assert engine._check_condition(cond, "Bash", {"command": "sudo rm"}) is True
        assert engine._check_condition(cond, "Bash", {"command": "rm sudo"}) is False

    def test_ends_with(self, engine):
        cond = make_condition(operator="ends_with", pattern=".py")
        assert engine._check_condition(cond, "Bash", {"command": "run script.py"}) is True
        assert engine._check_condition(cond, "Bash", {"command": "run script.sh"}) is False

    def test_unknown_operator_returns_false(self, engine):
        cond = make_condition(operator="nonexistent", pattern="x")
        assert engine._check_condition(cond, "Bash", {"command": "x"}) is False

    def test_none_field_value_returns_false(self, engine):
        cond = make_condition(field="nonexistent_field", operator="contains", pattern="x")
        assert engine._check_condition(cond, "Bash", {"command": "test"}) is False


# --- _extract_field ---

class TestExtractField:
    def test_direct_tool_input_field(self, engine):
        assert engine._extract_field("command", "Bash", {"command": "ls"}) == "ls"

    def test_bash_command_special_case(self, engine):
        assert engine._extract_field("command", "Bash", {}) == ""

    def test_write_content(self, engine):
        assert engine._extract_field("content", "Write", {"content": "hello"}) == "hello"

    def test_edit_new_string(self, engine):
        assert engine._extract_field("new_text", "Edit", {"new_string": "new"}) == "new"

    def test_edit_old_string(self, engine):
        assert engine._extract_field("old_text", "Edit", {"old_string": "old"}) == "old"

    def test_edit_file_path(self, engine):
        assert engine._extract_field("file_path", "Edit", {"file_path": "/tmp/f.py"}) == "/tmp/f.py"

    def test_edit_content_falls_back_to_new_string(self, engine):
        result = engine._extract_field("content", "Edit", {"new_string": "fallback"})
        assert result == "fallback"

    def test_multiedit_concatenates_edits(self, engine):
        tool_input = {"edits": [{"new_string": "a"}, {"new_string": "b"}]}
        result = engine._extract_field("content", "MultiEdit", tool_input)
        assert result == "a b"

    def test_multiedit_file_path(self, engine):
        result = engine._extract_field("file_path", "MultiEdit", {"file_path": "/f.py"})
        assert result == "/f.py"

    def test_stop_reason(self, engine):
        input_data = {"reason": "task complete"}
        result = engine._extract_field("reason", "Bash", {}, input_data)
        assert result == "task complete"

    def test_user_prompt(self, engine):
        input_data = {"user_prompt": "hello world"}
        result = engine._extract_field("user_prompt", "", {}, input_data)
        assert result == "hello world"

    def test_nonexistent_field_returns_none(self, engine):
        assert engine._extract_field("bogus", "UnknownTool", {}) is None

    def test_non_string_value_converted(self, engine):
        result = engine._extract_field("count", "Bash", {"count": 42})
        assert result == "42"


# --- _regex_match ---

class TestRegexMatch:
    def test_valid_match(self, engine):
        assert engine._regex_match(r"hello\s+world", "hello   world") is True

    def test_no_match(self, engine):
        assert engine._regex_match(r"^xyz$", "abc") is False

    def test_invalid_regex_returns_false(self, engine):
        assert engine._regex_match(r"[invalid", "text") is False


# --- _rule_matches ---

class TestRuleMatches:
    def test_no_conditions_returns_false(self, engine):
        rule = make_rule(conditions=[])
        assert engine._rule_matches(rule, {"tool_name": "Bash", "tool_input": {"command": "ls"}}) is False

    def test_tool_matcher_filters(self, engine):
        rule = make_rule(
            tool_matcher="Edit",
            conditions=[make_condition(field="file_path", operator="ends_with", pattern=".py")],
        )
        assert engine._rule_matches(rule, {"tool_name": "Bash", "tool_input": {"file_path": "f.py"}}) is False
        assert engine._rule_matches(rule, {"tool_name": "Edit", "tool_input": {"file_path": "f.py"}}) is True

    def test_all_conditions_must_match(self, engine):
        rule = make_rule(conditions=[
            make_condition(operator="contains", pattern="rm"),
            make_condition(operator="contains", pattern="-rf"),
        ])
        assert engine._rule_matches(rule, {"tool_name": "Bash", "tool_input": {"command": "rm -rf /"}}) is True
        assert engine._rule_matches(rule, {"tool_name": "Bash", "tool_input": {"command": "rm file"}}) is False


# --- evaluate_rules ---

class TestEvaluateRules:
    def test_no_match_returns_empty(self, engine):
        rule = make_rule(conditions=[make_condition(pattern="xyz_never_matches")])
        result = engine.evaluate_rules([rule], {"tool_name": "Bash", "tool_input": {"command": "ls"}})
        assert result == {}

    def test_warning_returns_system_message(self, engine):
        rule = make_rule(
            action="warn",
            message="Be careful!",
            conditions=[make_condition(operator="contains", pattern="rm")],
        )
        result = engine.evaluate_rules([rule], {"tool_name": "Bash", "tool_input": {"command": "rm file"}})
        assert "systemMessage" in result
        assert "Be careful!" in result["systemMessage"]

    def test_block_pretooluse_returns_deny(self, engine):
        rule = make_rule(
            action="block",
            message="Blocked!",
            conditions=[make_condition(operator="contains", pattern="rm")],
        )
        result = engine.evaluate_rules(
            [rule],
            {"tool_name": "Bash", "tool_input": {"command": "rm file"}, "hook_event_name": "PreToolUse"},
        )
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "Blocked!" in result["systemMessage"]

    def test_block_posttooluse_returns_deny(self, engine):
        rule = make_rule(
            action="block",
            message="Blocked!",
            conditions=[make_condition(operator="contains", pattern="rm")],
        )
        result = engine.evaluate_rules(
            [rule],
            {"tool_name": "Bash", "tool_input": {"command": "rm file"}, "hook_event_name": "PostToolUse"},
        )
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_block_stop_returns_decision_block(self, engine):
        rule = make_rule(
            action="block",
            message="Not done yet!",
            conditions=[make_condition(field="reason", operator="contains", pattern="done")],
        )
        result = engine.evaluate_rules(
            [rule],
            {"tool_name": "", "tool_input": {}, "hook_event_name": "Stop", "reason": "I'm done"},
        )
        assert result["decision"] == "block"
        assert "Not done yet!" in result["reason"]

    def test_block_other_event_returns_system_message_only(self, engine):
        rule = make_rule(
            action="block",
            message="Blocked!",
            conditions=[make_condition(operator="contains", pattern="test")],
        )
        result = engine.evaluate_rules(
            [rule],
            {"tool_name": "Bash", "tool_input": {"command": "test"}, "hook_event_name": "UserPromptSubmit"},
        )
        assert "systemMessage" in result
        assert "hookSpecificOutput" not in result

    def test_blocking_rules_take_priority_over_warnings(self, engine):
        warn_rule = make_rule(
            name="warn-rule",
            action="warn",
            message="Warning!",
            conditions=[make_condition(operator="contains", pattern="rm")],
        )
        block_rule = make_rule(
            name="block-rule",
            action="block",
            message="Blocked!",
            conditions=[make_condition(operator="contains", pattern="rm")],
        )
        result = engine.evaluate_rules(
            [warn_rule, block_rule],
            {"tool_name": "Bash", "tool_input": {"command": "rm file"}, "hook_event_name": "PreToolUse"},
        )
        # Block should win
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "Blocked!" in result["systemMessage"]
        # Warning message should NOT be included (blocking takes priority)
        assert "Warning!" not in result["systemMessage"]

    def test_multiple_warnings_combined(self, engine):
        rule1 = make_rule(
            name="rule1",
            message="Warning 1",
            conditions=[make_condition(operator="contains", pattern="rm")],
        )
        rule2 = make_rule(
            name="rule2",
            message="Warning 2",
            conditions=[make_condition(operator="contains", pattern="rm")],
        )
        result = engine.evaluate_rules(
            [rule1, rule2],
            {"tool_name": "Bash", "tool_input": {"command": "rm file"}},
        )
        assert "Warning 1" in result["systemMessage"]
        assert "Warning 2" in result["systemMessage"]
