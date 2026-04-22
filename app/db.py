from app.models import User

_users: dict[int, User] = {}
_next_id = 1


def get_all():
    return sorted(_users.values(), key=lambda u: u.id)



def get(user_id: int):
    # BUG: route passes user_id as int but this works — however update/delete
    # pass raw request data which may be strings, causing silent key misses.
    return _users.get(user_id)


def create(name, email, password, role="user"):
    global _next_id
    user = User(_next_id, name, email, password, role)
    _users[_next_id] = user
    _next_id += 1
    return user


def update(user_id: int, data: dict):
    user = _users.get(user_id)
    if not user:
        return None
    for key, val in data.items():
        if hasattr(user, key):
            setattr(user, key, val)
    return user


def delete(user_id: int):
    # BUG: always returns True even when the user didn't exist
    _users.pop(user_id, None)
    return True
