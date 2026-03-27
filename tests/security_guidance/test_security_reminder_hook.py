"""Tests for security reminder hook."""

import json
import os
import time
import tempfile
import pytest

# Import from the hook module
import security_reminder_hook as hook


# --- check_patterns ---

class TestCheckPatterns:
    def test_github_actions_workflow_yml(self):
        rule, reminder = hook.check_patterns(".github/workflows/ci.yml", "")
        assert rule == "github_actions_workflow"
        assert reminder is not None

    def test_github_actions_workflow_yaml(self):
        rule, _ = hook.check_patterns(".github/workflows/deploy.yaml", "")
        assert rule == "github_actions_workflow"

    def test_github_actions_non_workflow_ignored(self):
        rule, _ = hook.check_patterns(".github/workflows/README.md", "")
        assert rule is None

    def test_child_process_exec(self):
        rule, _ = hook.check_patterns("app.js", "child_process.exec(cmd)")
        assert rule == "child_process_exec"

    def test_exec_sync(self):
        rule, _ = hook.check_patterns("app.js", "execSync(cmd)")
        assert rule == "child_process_exec"

    def test_new_function_injection(self):
        rule, _ = hook.check_patterns("app.js", "new Function(code)")
        assert rule == "new_function_injection"

    def test_eval_injection(self):
        rule, _ = hook.check_patterns("app.js", "eval(userInput)")
        assert rule == "eval_injection"

    def test_dangerously_set_inner_html(self):
        rule, _ = hook.check_patterns("App.tsx", "dangerouslySetInnerHTML={{__html: data}}")
        assert rule == "react_dangerously_set_html"

    def test_document_write(self):
        rule, _ = hook.check_patterns("page.js", "document.write(html)")
        assert rule == "document_write_xss"

    def test_inner_html_equals(self):
        rule, _ = hook.check_patterns("page.js", 'el.innerHTML = userInput')
        assert rule == "innerHTML_xss"

    def test_inner_html_equals_no_space(self):
        rule, _ = hook.check_patterns("page.js", 'el.innerHTML=userInput')
        assert rule == "innerHTML_xss"

    def test_pickle(self):
        rule, _ = hook.check_patterns("app.py", "import pickle")
        assert rule == "pickle_deserialization"

    def test_os_system(self):
        rule, _ = hook.check_patterns("app.py", "os.system(cmd)")
        assert rule == "os_system_injection"

    def test_from_os_import_system(self):
        rule, _ = hook.check_patterns("app.py", "from os import system")
        assert rule == "os_system_injection"

    def test_safe_code_no_match(self):
        rule, _ = hook.check_patterns("app.py", "print('hello world')")
        assert rule is None

    def test_path_normalization(self):
        # Leading slashes should be stripped
        rule, _ = hook.check_patterns("/.github/workflows/ci.yml", "")
        assert rule == "github_actions_workflow"


# --- extract_content_from_input ---

class TestExtractContentFromInput:
    def test_write_tool(self):
        result = hook.extract_content_from_input("Write", {"content": "eval(x)"})
        assert result == "eval(x)"

    def test_edit_tool(self):
        result = hook.extract_content_from_input("Edit", {"new_string": "eval(x)"})
        assert result == "eval(x)"

    def test_multiedit_tool(self):
        result = hook.extract_content_from_input(
            "MultiEdit", {"edits": [{"new_string": "a"}, {"new_string": "b"}]}
        )
        assert result == "a b"

    def test_multiedit_empty_edits(self):
        result = hook.extract_content_from_input("MultiEdit", {"edits": []})
        assert result == ""

    def test_unknown_tool(self):
        result = hook.extract_content_from_input("Bash", {"command": "ls"})
        assert result == ""


# --- load_state / save_state ---

class TestStateManagement:
    def test_load_missing_file_returns_empty_set(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hook, "get_state_file", lambda sid: str(tmp_path / "missing.json"))
        result = hook.load_state("test-session")
        assert result == set()

    def test_save_and_load_roundtrip(self, tmp_path, monkeypatch):
        state_file = str(tmp_path / "state.json")
        monkeypatch.setattr(hook, "get_state_file", lambda sid: state_file)
        warnings = {"file1-rule1", "file2-rule2"}
        hook.save_state("test-session", warnings)
        loaded = hook.load_state("test-session")
        assert loaded == warnings

    def test_load_corrupt_json_returns_empty(self, tmp_path, monkeypatch):
        state_file = tmp_path / "corrupt.json"
        state_file.write_text("{invalid json")
        monkeypatch.setattr(hook, "get_state_file", lambda sid: str(state_file))
        result = hook.load_state("test-session")
        assert result == set()


# --- cleanup_old_state_files ---

class TestCleanupOldStateFiles:
    def test_removes_old_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr(os.path, "expanduser", lambda p: str(tmp_path) if p == "~/.claude" else p)
        # Create an old state file
        old_file = tmp_path / "security_warnings_state_old.json"
        old_file.write_text("[]")
        # Set mtime to 31 days ago
        old_time = time.time() - (31 * 24 * 60 * 60)
        os.utime(str(old_file), (old_time, old_time))

        # Create a recent state file
        new_file = tmp_path / "security_warnings_state_new.json"
        new_file.write_text("[]")

        hook.cleanup_old_state_files()

        assert not old_file.exists()
        assert new_file.exists()

    def test_ignores_non_state_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr(os.path, "expanduser", lambda p: str(tmp_path) if p == "~/.claude" else p)
        other_file = tmp_path / "settings.json"
        other_file.write_text("{}")
        old_time = time.time() - (31 * 24 * 60 * 60)
        os.utime(str(other_file), (old_time, old_time))

        hook.cleanup_old_state_files()
        assert other_file.exists()
