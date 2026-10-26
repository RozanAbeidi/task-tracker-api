"""Unit tests for the Task Tracker API. Run with:  python -m pytest"""

import json
import os
import sys

import azure.functions as func
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import function_app  # noqa: E402

# The @app.route decorator wraps each function; this gets the plain Python function back.
list_tasks = function_app.list_tasks.build().get_user_function()
create_task = function_app.create_task.build().get_user_function()
update_task = function_app.update_task.build().get_user_function()
delete_task = function_app.delete_task.build().get_user_function()


def make_request(method, url, body=None, route_params=None, raw_body=None):
    if raw_body is None:
        raw_body = json.dumps(body).encode() if body is not None else b""
    return func.HttpRequest(
        method=method, url=url, body=raw_body, route_params=route_params or {}
    )


@pytest.fixture(autouse=True)
def clear_tasks():
    """Start every test with an empty task list."""
    function_app.tasks.clear()


def add_task(title="Buy milk"):
    response = create_task(make_request("POST", "/api/tasks", {"title": title}))
    return json.loads(response.get_body())


def test_list_is_empty_at_start():
    response = list_tasks(make_request("GET", "/api/tasks"))
    assert response.status_code == 200
    assert json.loads(response.get_body()) == []


def test_create_task():
    response = create_task(make_request("POST", "/api/tasks", {"title": "  Buy milk  "}))
    task = json.loads(response.get_body())
    assert response.status_code == 201
    assert task["title"] == "Buy milk"  # surrounding spaces trimmed
    assert task["done"] is False


def test_create_task_requires_title():
    response = create_task(make_request("POST", "/api/tasks", {"title": "   "}))
    assert response.status_code == 400


def test_create_task_rejects_invalid_json():
    response = create_task(make_request("POST", "/api/tasks", raw_body=b"not json"))
    assert response.status_code == 400


def test_create_task_rejects_long_title():
    response = create_task(make_request("POST", "/api/tasks", {"title": "x" * 201}))
    assert response.status_code == 400


def test_update_task_marks_done():
    task = add_task()
    response = update_task(
        make_request("PATCH", f"/api/tasks/{task['id']}", {"done": True}, {"task_id": task["id"]})
    )
    assert response.status_code == 200
    assert json.loads(response.get_body())["done"] is True


def test_update_task_rejects_non_boolean_done():
    task = add_task()
    response = update_task(
        make_request("PATCH", f"/api/tasks/{task['id']}", {"done": "yes"}, {"task_id": task["id"]})
    )
    assert response.status_code == 400


def test_update_missing_task_returns_404():
    response = update_task(
        make_request("PATCH", "/api/tasks/nope", {"done": True}, {"task_id": "nope"})
    )
    assert response.status_code == 404


def test_delete_task():
    task = add_task()
    response = delete_task(
        make_request("DELETE", f"/api/tasks/{task['id']}", route_params={"task_id": task["id"]})
    )
    assert response.status_code == 204
    assert function_app.tasks == {}


def test_delete_missing_task_returns_404():
    response = delete_task(make_request("DELETE", "/api/tasks/nope", route_params={"task_id": "nope"}))
    assert response.status_code == 404
