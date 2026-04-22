from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash


class User:
    def __init__(self, id, name, email, password, role="user"):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role
        self.created_at = datetime.now().isoformat()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
        }
