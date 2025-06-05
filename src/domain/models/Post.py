from dataclasses import dataclass
import datetime


@dataclass
class Post:
    Post_date: datetime
    Post_Url: str
    Discipline_id: int
