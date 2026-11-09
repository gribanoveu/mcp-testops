"""Shared fixtures: a mocked TestOps stand and a package reloaded with other env."""

import importlib
import os

import httpx
import pytest

import mcp_testops
from mcp_testops import client as testops_client

# Reload order matters: config reads env, the rest build on it, tools register on the
# server object, and only then the package re-exports the fresh names.
MODULES = (
    "config",
    "client",
    "helpers",
    "bodies",
    "server",
    "tools.projects",
    "tools.cases",
    "tools.plans",
    "tools.launches",
    "tools.references",
    "tools",
)


def _reload_package() -> type:
    for name in MODULES:
        importlib.reload(importlib.import_module(f"mcp_testops.{name}"))
    return importlib.reload(mcp_testops)


@pytest.fixture
def api():
    """Install a MockTransport as the stand; the tool code cannot tell the difference.

    Until install() is called the client refuses every request, so a forgotten
    handler fails the test instead of reaching the real stand.
    """

    def refuse(request):
        pytest.fail(f"api fixture: no handler installed, request went out to {request.url}")

    testops_client._client = httpx.Client(
        transport=httpx.MockTransport(refuse), base_url="http://testops.test"
    )
    installed: list[httpx.Client] = []

    def install(handler) -> httpx.Client:
        client = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://testops.test")
        testops_client._client = client
        installed.append(client)
        return client

    yield install
    assert installed, "the api fixture was requested but install() was never called"
    testops_client._client = None
    for client in installed:
        client.close()


@pytest.fixture
def fresh():
    """Reload the package with the given env, so import-time flags take effect."""
    saved = dict(os.environ)

    def load(**env) -> type:
        for key, value in env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        return _reload_package()

    yield load
    os.environ.clear()
    os.environ.update(saved)
    _reload_package()
