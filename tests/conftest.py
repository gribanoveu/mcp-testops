"""Shared fixtures: a mocked TestOps stand and a module reloaded with other env."""

import importlib
import os

import httpx
import pytest

import mcp_testops


@pytest.fixture
def api():
    """Install a MockTransport as the stand; the tool code cannot tell the difference.

    Until install() is called the client refuses every request, so a forgotten
    handler fails the test instead of reaching the real stand.
    """

    def refuse(request):
        pytest.fail(f"api fixture: no handler installed, request went out to {request.url}")

    mcp_testops._client = httpx.Client(
        transport=httpx.MockTransport(refuse), base_url="http://testops.test"
    )
    installed: list[httpx.Client] = []

    def install(handler) -> httpx.Client:
        client = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://testops.test")
        mcp_testops._client = client
        installed.append(client)
        return client

    yield install
    assert installed, "the api fixture was requested but install() was never called"
    mcp_testops._client = None
    for client in installed:
        client.close()


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
