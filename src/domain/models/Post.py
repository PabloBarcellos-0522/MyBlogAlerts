from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Post:
    Post_date: datetime.date
    Post_Url: str
    Discipline_id: int
    Content: str
    idPost: Optional[int] = None
