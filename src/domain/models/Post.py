from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Post:
    post_date: datetime.date
    post_url: str
    discipline_id: int
    content: str
    id_post: Optional[int] = None
