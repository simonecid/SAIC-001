from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Task:
    title: str
    done: bool = False
    priority: int = 1  # 1=low, 2=medium, 3=high
    tags: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def mark_done(self):
        # BUG: sets done=True but never records completed_at,
        # so there's no way to know when a task was finished.
        self.done = True

    def is_high_priority(self):
        return self.priority >= 3

    def to_dict(self):
        return {
            "title": self.title,
            "done": self.done,
            "priority": self.priority,
            "tags": self.tags,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
