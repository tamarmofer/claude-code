"""Tests for hookify config loader."""

import os
import tempfile
import pytest
from hookify.core.config_loader import (
    Condition,
    Rule,
    extract_frontmatter,
    load_rule_file,
    load_rules,
)


# --- extract_frontmatter ---

class TestExtractFrontmatter:
    def test_simple_key_value(self):
        content = "---\nname: test-rule\nevent: bash\n---\nHello"
        fm, msg = extract_frontmatter(content)
        assert fm["name"] == "test-rule"
        assert fm["event"] == "bash"
        assert msg == "Hello"

    def test_boolean_true(self):
        content = "---\nenabled: true\n---\n"
        fm, _ = extract_frontmatter(content)
        assert fm["enabled"] is True

    def test_boolean_false(self):
        content = "---\nenabled: false\n---\n"
        fm, _ = extract_frontmatter(content)
        assert fm["enabled"] is False

    def test_quoted_value_stripped(self):
        content = '---\nname: "my-rule"\n---\n'
        fm, _ = extract_frontmatter(content)
        assert fm["name"] == "my-rule"

    def test_single_quoted_value_stripped(self):
        content = "---\nname: 'my-rule'\n---\n"
        fm, _ = extract_frontmatter(content)
        assert fm["name"] == "my-rule"

    def test_simple_list_items(self):
        content = "---\ntags:\n  - alpha\n  - beta\n---\n"
        fm, _ = extract_frontmatter(content)
        assert fm["tags"] == ["alpha", "beta"]

    def test_inline_dict_list(self):
        content = "---\nconditions:\n  - field: command, operator: contains, pattern: rm\n---\n"
        fm, _ = extract_frontmatter(content)
        assert len(fm["conditions"]) == 1
        assert fm["conditions"][0]["field"] == "command"
        assert fm["conditions"][0]["operator"] == "contains"
        assert fm["conditions"][0]["pattern"] == "rm"

    def test_multiline_dict_list(self):
        content = "---\nconditions:\n  - field: command\n    operator: regex_match\n    pattern: rm\n---\n"
        fm, _ = extract_frontmatter(content)
        assert len(fm["conditions"]) == 1
        assert fm["conditions"][0]["field"] == "command"
        assert fm["conditions"][0]["operator"] == "regex_match"

    def test_multiple_multiline_dict_items(self):
        content = (
            "---\nconditions:\n"
            "  - field: command\n    operator: contains\n    pattern: rm\n"
            "  - field: command\n    operator: not_contains\n    pattern: dry-run\n"
            "---\n"
        )
        fm, _ = extract_frontmatter(content)
        assert len(fm["conditions"]) == 2
        assert fm["conditions"][0]["pattern"] == "rm"
        assert fm["conditions"][1]["operator"] == "not_contains"

    def test_comments_ignored(self):
        content = "---\n# This is a comment\nname: test\n---\n"
        fm, _ = extract_frontmatter(content)
        assert fm["name"] == "test"
        assert "#" not in fm

    def test_empty_lines_ignored(self):
        content = "---\nname: test\n\nevent: bash\n---\n"
        fm, _ = extract_frontmatter(content)
        assert fm["name"] == "test"
        assert fm["event"] == "bash"

    def test_no_frontmatter_markers(self):
        content = "Just plain text"
        fm, msg = extract_frontmatter(content)
        assert fm == {}
        assert msg == "Just plain text"

    def test_incomplete_frontmatter(self):
        content = "---\nname: test\nNo closing marker"
        fm, msg = extract_frontmatter(content)
        assert fm == {}

    def test_message_body_stripped(self):
        content = "---\nname: test\n---\n\n  Warning message  \n\n"
        _, msg = extract_frontmatter(content)
        assert msg == "Warning message"


# --- Condition.from_dict ---

class TestConditionFromDict:
    def test_basic(self):
        c = Condition.from_dict({"field": "command", "operator": "contains", "pattern": "rm"})
        assert c.field == "command"
        assert c.operator == "contains"
        assert c.pattern == "rm"

    def test_defaults(self):
        c = Condition.from_dict({})
        assert c.field == ""
        assert c.operator == "regex_match"
        assert c.pattern == ""


# --- Rule.from_dict ---

class TestRuleFromDict:
    def test_new_style_conditions(self):
        fm = {
            "name": "test",
            "enabled": True,
            "event": "bash",
            "conditions": [
                {"field": "command", "operator": "contains", "pattern": "rm"},
            ],
        }
        rule = Rule.from_dict(fm, "Danger!")
        assert rule.name == "test"
        assert len(rule.conditions) == 1
        assert rule.conditions[0].field == "command"
        assert rule.message == "Danger!"

    def test_legacy_pattern_bash(self):
        fm = {"name": "test", "event": "bash", "pattern": "rm -rf"}
        rule = Rule.from_dict(fm, "msg")
        assert len(rule.conditions) == 1
        assert rule.conditions[0].field == "command"
        assert rule.conditions[0].operator == "regex_match"
        assert rule.conditions[0].pattern == "rm -rf"

    def test_legacy_pattern_file(self):
        fm = {"name": "test", "event": "file", "pattern": "eval\\("}
        rule = Rule.from_dict(fm, "msg")
        assert rule.conditions[0].field == "new_text"

    def test_legacy_pattern_other_event(self):
        fm = {"name": "test", "event": "all", "pattern": "test"}
        rule = Rule.from_dict(fm, "msg")
        assert rule.conditions[0].field == "content"

    def test_defaults(self):
        rule = Rule.from_dict({}, "msg")
        assert rule.name == "unnamed"
        assert rule.enabled is True
        assert rule.action == "warn"
        assert rule.event == "all"

    def test_conditions_take_precedence_over_legacy_pattern(self):
        fm = {
            "name": "test",
            "pattern": "legacy",
            "conditions": [{"field": "command", "operator": "contains", "pattern": "new"}],
        }
        rule = Rule.from_dict(fm, "msg")
        assert len(rule.conditions) == 1
        assert rule.conditions[0].pattern == "new"


# --- load_rule_file ---

class TestLoadRuleFile:
    def test_valid_file(self, tmp_path):
        rule_file = tmp_path / "hookify.test.local.md"
        rule_file.write_text("---\nname: test\nenabled: true\nevent: bash\npattern: rm\n---\nDanger!")
        rule = load_rule_file(str(rule_file))
        assert rule is not None
        assert rule.name == "test"

    def test_missing_frontmatter(self, tmp_path):
        rule_file = tmp_path / "hookify.test.local.md"
        rule_file.write_text("No frontmatter here")
        rule = load_rule_file(str(rule_file))
        assert rule is None

    def test_nonexistent_file(self):
        rule = load_rule_file("/nonexistent/path/rule.md")
        assert rule is None


# --- load_rules ---

class TestLoadRules:
    def test_loads_from_dot_claude_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "hookify.test.local.md").write_text(
            "---\nname: test\nenabled: true\nevent: bash\npattern: rm\n---\nDanger!"
        )
        rules = load_rules(event="bash")
        assert len(rules) == 1
        assert rules[0].name == "test"

    def test_event_filtering(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "hookify.bash-rule.local.md").write_text(
            "---\nname: bash-rule\nenabled: true\nevent: bash\npattern: rm\n---\nmsg"
        )
        (claude_dir / "hookify.file-rule.local.md").write_text(
            "---\nname: file-rule\nenabled: true\nevent: file\npattern: eval\n---\nmsg"
        )
        bash_rules = load_rules(event="bash")
        assert all(r.event == "bash" for r in bash_rules)

    def test_disabled_rules_excluded(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "hookify.disabled.local.md").write_text(
            "---\nname: disabled\nenabled: false\nevent: bash\npattern: rm\n---\nmsg"
        )
        rules = load_rules()
        assert len(rules) == 0

    def test_all_event_matches_any_filter(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "hookify.all-rule.local.md").write_text(
            "---\nname: all-rule\nenabled: true\nevent: all\npattern: test\n---\nmsg"
        )
        rules = load_rules(event="bash")
        assert len(rules) == 1

    def test_no_files_returns_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rules = load_rules()
        assert rules == []
