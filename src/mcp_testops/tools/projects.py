"""Tools: projects."""

from ..client import _api, _paged
from ..config import DEFAULT_PAGE_SIZE
from ..helpers import _guard, _pick
from ..server import mcp


@mcp.tool()
@_guard
def list_projects(
    search: str = "",
    favorite: bool = False,
    page: int = 0,
    size: int = DEFAULT_PAGE_SIZE,
) -> str:
    """List TestOps projects, ordered by name.

    search: optional substring of the project name; favorite: only starred projects.
    page starts at 0, size is capped at 100. Returns {content, totalElements, totalPages, number}
    with id, name, abbr, isPublic, isVersioned, launchCount, automationPercent per project.
    """
    res = _paged(
        "/api/project",
        {"search": search or None, "favorite": True if favorite else None},
        page=page,
        size=size,
        sort="name,ASC",
    )
    res["content"] = [
        _pick(item, ("id", "name", "abbr", "isPublic", "isVersioned", "launchCount", "automationPercent"))
        for item in res["content"]
    ]
    return {"ok": True, **res}


@mcp.tool()
@_guard
def get_project(project_id: int) -> str:
    """Get one project by id: id, name, abbr, isPublic, isVersioned, launchCount, automationPercent."""
    data = _api("GET", f"/api/project/{project_id}")
    keys = ("id", "name", "abbr", "isPublic", "isVersioned", "launchCount", "automationPercent",
            "createdDate", "lastModifiedDate")
    return {"ok": True, **_pick(data, keys)}
