# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app
python run.py

# Run all tests
python -m pytest tests/ -v

# Run a single test
python -m pytest tests/test_routes.py::test_create_returns_201 -v

# Build Docker image
docker build -t user-api:latest .

# Deploy to INT
kubectl --kubeconfig int.yaml apply -f k8s/int/

# Deploy to PROD
kubectl --kubeconfig int.yaml apply -f k8s/prod/
```

## Architecture

The app is a Flask REST API for user management. `run.py` calls `app/app.py:create_app()`, which registers a single Blueprint from `app/routes.py` at `/api/users`. Routes delegate all persistence to `app/db.py`, which holds an in-memory dict (`_users`) and a module-level auto-increment counter (`_next_id`). `app/models.py` is a plain class with no ORM.

Because `db.py` is stateful at the module level, tests must reset `db._users` and `db._next_id` in a fixture before each run — see the `reset_db` autouse fixture in `tests/test_routes.py`.

## Known bugs

These bugs are intentional (test bed for lifecycle hooks). Tests in `tests/test_routes.py` document each one:

| Location | Bug |
|---|---|
| `routes.py` `GET /<id>` | Returns all users instead of the requested one |
| `routes.py` `POST /` | Missing validation — unhandled `KeyError` → 500 |
| `db.py` `delete()` | Always returns 200, never 404 |
| `models.py` | Password stored in plaintext and returned in every response |

## Lifecycle hooks

Every tool call Claude makes is logged to `lifecycle.log` in the project root. The hooks are registered in `.claude/settings.json` and implemented in `hooks/`:

- `hooks/pre_tool.sh` — fires before each tool, logs tool name and key input field
- `hooks/post_tool.sh` — fires after each tool, logs ok/error status
- `hooks/stop.sh` — fires when Claude finishes a turn, logs session ID

All hooks exit 0 (non-blocking). To inspect events: `cat lifecycle.log`.

## Environments

| Env | Replicas | Image tag | `imagePullPolicy` |
|---|---|---|---|
| INT | 1 | `user-api:latest` | `Never` (local build) |
| PROD | 2 | `user-api:v1.0.0` | default |

The kubeconfig for both environments is `int.yaml` (points to `https://127.0.0.1:6443`).
