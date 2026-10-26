# Task Tracker API

A small serverless REST API built with **Python** and **Azure Functions**. It lets you create, list, update, and delete tasks, with input validation, consistent JSON error responses, logging, and unit tests.

## Tech used
- Python 3.11
- Azure Functions (Python v2 programming model)
- pytest for unit tests
- Planned: Azure SQL for storage, and a GitHub Actions pipeline for automatic deployment

## Endpoints

| Method | Route | What it does |
| --- | --- | --- |
| GET | `/api/tasks` | List all tasks |
| POST | `/api/tasks` | Create a task. Body: `{"title": "Buy milk"}` |
| PATCH | `/api/tasks/{id}` | Update a task. Body: `{"title": "...", "done": true}` |
| DELETE | `/api/tasks/{id}` | Delete a task |

Errors always come back in the same shape, for example `{"error": "Task not found"}` with a 404 status.

## Run it locally

1. Install [Python 3.11](https://www.python.org/downloads/) and the [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local).
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```
3. Copy the example settings file:
   ```bash
   cp local.settings.example.json local.settings.json
   ```
4. Start the API:
   ```bash
   func start
   ```
5. Try it from another terminal:
   ```bash
   curl -X POST http://localhost:7071/api/tasks -H "Content-Type: application/json" -d '{"title": "Buy milk"}'
   curl http://localhost:7071/api/tasks
   ```

## Run the tests
```bash
python -m pytest
```

## Roadmap
- [x] REST endpoints with validation and error handling
- [x] Unit tests
- [ ] Store tasks in Azure SQL instead of memory
- [ ] CI/CD pipeline that tests and deploys on every push to `main`
- [ ] Deploy to Azure and link the live API here
