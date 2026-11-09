"""Shared fixtures: a mocked TestOps stand and a module reloaded with other env."""

import importlib
import os

import httpx
import pytest

import mcp_testops


@pytest.fixture
def api():
    """Install a MockTransport as the stand; the tool code cannot tell the difference."""

    def install(handler) -> httpx.Client:
        client = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://testops.test")
        mcp_testops._client = client
        return client

    yield install
    mcp_testops._client = None


@pytest.fixture
def fresh():
    """Reload the module with the given env, so registration-time flags take effect."""
    saved = dict(os.environ)

    def load(**env) -> type:
        for key, value in env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        return importlib.reload(mcp_testops)

    yield load
    os.environ.clear()
    os.environ.update(saved)
    importlib.reload(mcp_testops)
