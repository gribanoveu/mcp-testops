"""The `call` subcommand: one tool from the shell, no MCP client.

These tests start a real server subprocess the way the CLI does, so they check the thing a
user actually runs. Nothing here reaches the stand: the cases stop before a request
(`--list`, `--schema`, broken arguments, a missing required argument).
"""

import os
import subprocess
import sys

BASE_ENV = {**os.environ, "TESTOPS_TOKEN": "test", "TESTOPS_BASE_URL": "http://testops.test"}


def call(*argv: str, **env: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "mcp_testops", "call", *argv],
        capture_output=True,
        text=True,
        timeout=120,
        env={**BASE_ENV, **env},
    )


def test_call_lists_every_tool():
    result = call("--list")
    assert result.returncode == 0
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 30
    assert any(line.startswith("list_projects\t") for line in lines)


def test_call_prints_the_argument_schema():
    result = call("--schema", "get_launch_statistic")
    assert result.returncode == 0
    assert '"launch_id"' in result.stdout


def test_call_rejects_unknown_tool_schema():
    result = call("--schema", "no_such_tool")
    assert result.returncode == 1
    assert "no such tool" in result.stderr


def test_call_rejects_arguments_that_are_not_json():
    result = call("list_projects", "search=wowtax")
    assert result.returncode == 1
    assert "arguments are not JSON" in result.stderr


def test_call_reports_a_missing_required_argument_with_exit_code():
    result = call("get_project", "{}")
    assert result.returncode == 1
    assert "project_id" in result.stdout + result.stderr


def test_call_refuses_to_start_without_a_token():
    result = call("--list", TESTOPS_TOKEN="")
    assert result.returncode == 1
    assert "TESTOPS_TOKEN is not set" in result.stderr
    # The hint has to be actionable: the agent reads it in a terminal and has to know what to set.
    assert "export TESTOPS_TOKEN" in result.stderr
    assert "TESTOPS_BASE_URL" in result.stderr
    assert "Per command" in result.stderr
