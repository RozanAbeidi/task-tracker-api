"""Task Tracker API - a small serverless REST API built with Azure Functions (Python).

Endpoints (all under /api):
    GET    /tasks         list all tasks
    POST   /tasks         create a task   body: {"title": "Buy milk"}
    PATCH  /tasks/{id}    update a task   body: {"title": "...", "done": true}
    DELETE /tasks/{id}    delete a task

Storage is in memory for now (it resets when the app restarts).
A later step swaps this for a real database (Azure SQL).
"""

import json
import logging
import uuid

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

MAX_TITLE_LENGTH = 200

# In-memory storage: { task_id: {"id": ..., "title": ..., "done": ...} }
tasks: dict[str, dict] = {}


def json_response(body, status: int = 200) -> func.HttpResponse:
    """Return a JSON HTTP response."""
    return func.HttpResponse(
        json.dumps(body), status_code=status, mimetype="application/json"
    )


def error(message: str, status: int) -> func.HttpResponse:
    """Return a JSON error response in one consistent shape."""
    return json_response({"error": message}, status)


def read_json_body(req: func.HttpRequest):
    """Parse the request body as a JSON object, or return None if it is invalid."""
    try:
        data = req.get_json()
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def validate_title(title):
    """Return (clean_title, error_message). Exactly one of them is None."""
    if not isinstance(title, str) or not title.strip():
        return None, "'title' is required and must be a non-empty string"
    title = title.strip()
    if len(title) > MAX_TITLE_LENGTH:
        return None, f"'title' must be {MAX_TITLE_LENGTH} characters or fewer"
    return title, None


@app.route(route="tasks", methods=["GET"])
def list_tasks(req: func.HttpRequest) -> func.HttpResponse:
    return json_response(list(tasks.values()))


@app.route(route="tasks", methods=["POST"])
def create_task(req: func.HttpRequest) -> func.HttpResponse:
    data = read_json_body(req)
    if data is None:
        return error("Request body must be a JSON object", 400)

    title, problem = validate_title(data.get("title"))
    if problem:
        return error(problem, 400)

    task = {"id": str(uuid.uuid4()), "title": title, "done": False}
    tasks[task["id"]] = task
    logging.info("Created task %s", task["id"])
    return json_response(task, 201)


@app.route(route="tasks/{task_id}", methods=["PATCH"])
def update_task(req: func.HttpRequest) -> func.HttpResponse:
    task_id = req.route_params.get("task_id")
    task = tasks.get(task_id)
    if task is None:
        return error("Task not found", 404)

    data = read_json_body(req)
    if data is None:
        return error("Request body must be a JSON object", 400)

    if "title" in data:
        title, problem = validate_title(data["title"])
        if problem:
            return error(problem, 400)
        task["title"] = title

    if "done" in data:
        if not isinstance(data["done"], bool):
            return error("'done' must be true or false", 400)
        task["done"] = data["done"]

    logging.info("Updated task %s", task_id)
    return json_response(task)


@app.route(route="tasks/{task_id}", methods=["DELETE"])
def delete_task(req: func.HttpRequest) -> func.HttpResponse:
    task_id = req.route_params.get("task_id")
    if tasks.pop(task_id, None) is None:
        return error("Task not found", 404)

    logging.info("Deleted task %s", task_id)
    return func.HttpResponse(status_code=204)
