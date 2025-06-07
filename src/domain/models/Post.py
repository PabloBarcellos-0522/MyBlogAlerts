from dataclasses import dataclass
from datetime import datetime


@dataclass
class Post:
    idPost: int
    Post_date: datetime
    Post_Url: str
    Discipline_id: int
