# user-api

A intentionally buggy Flask user management API used as a test bed for Claude Code lifecycle hooks.

## Project structure

```
.
├── app/
│   ├── app.py        # Flask application factory
│   ├── db.py         # In-memory user store
│   ├── models.py     # User model
│   └── routes.py     # REST endpoints
├── hooks/
│   ├── pre_tool.sh   # Logs PreToolUse events
│   ├── post_tool.sh  # Logs PostToolUse events
│   └── stop.sh       # Logs Stop events
├── k8s/
│   ├── int/          # Kubernetes manifests for INT
│   └── prod/         # Kubernetes manifests for PROD
├── .claude/
│   └── settings.json # Hook registration
├── Dockerfile
├── requirements.txt
└── run.py            # Entry point
```

## Running locally

```bash
pip install -r requirements.txt
python run.py
```

The API listens on `http://localhost:5000`.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/users | List all users |
| GET | /api/users/:id | Get a single user |
| POST | /api/users | Create a user |
| PUT | /api/users/:id | Update a user |
| DELETE | /api/users/:id | Delete a user |

### Example requests

```bash
# Create a user
curl -s -X POST http://localhost:5000/api/users \
  -H 'Content-Type: application/json' \
  -d '{"name": "Alice", "email": "alice@example.com", "password": "secret"}'

# List users
curl -s http://localhost:5000/api/users

# Get user by id
curl -s http://localhost:5000/api/users/1

# Update user
curl -s -X PUT http://localhost:5000/api/users/1 \
  -H 'Content-Type: application/json' \
  -d '{"role": "admin"}'

# Delete user
curl -s -X DELETE http://localhost:5000/api/users/1
```

## Known bugs

| Location | Bug |
|----------|-----|
| `models.py` | Password stored in plaintext and returned in every API response |
| `routes.py` `GET /api/users/:id` | Returns all users instead of the requested one |
| `routes.py` `POST /api/users` | No input validation — missing fields raise an unhandled `KeyError` (HTTP 500) |
| `db.py` `delete()` | Always returns success even when the user ID does not exist |

## Lifecycle hooks

When Claude Code works in this directory, every tool call is logged to `lifecycle.log`:

```
2026-04-21T10:00:01+00:00 [PreToolUse]  tool=Read file_path=app/routes.py
2026-04-21T10:00:01+00:00 [PostToolUse] tool=Read status=ok
2026-04-21T10:00:02+00:00 [PreToolUse]  tool=Edit file_path=app/routes.py
2026-04-21T10:00:02+00:00 [PostToolUse] tool=Edit status=ok
2026-04-21T10:00:05+00:00 [Stop]        session=abc123...
```

Hook scripts live in `hooks/` and are registered in `.claude/settings.json`.

## Deployment

The app is deployed to a k3s cluster using the kubeconfig in `int.yaml`.

```bash
# INT
kubectl --kubeconfig int.yaml apply -f k8s/int/

# PROD
kubectl --kubeconfig int.yaml apply -f k8s/prod/
```

INT runs 1 replica with `imagePullPolicy: Never` (local image). PROD runs 2 replicas and expects a versioned image tag (`user-api:v1.0.0`).
