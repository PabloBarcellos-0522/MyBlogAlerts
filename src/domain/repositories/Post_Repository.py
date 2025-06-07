from datetime import datetime
from typing import List
from src.domain.models.Discipline import Discipline
from src.domain.models.Post import Post
from abc import ABC, abstractmethod


class PostRepository(ABC):
    @abstractmethod
    def save(self, post: Post) -> None: pass

    @abstractmethod
    def get_posts(self) -> List[tuple]: pass

    @abstractmethod
    def change_post_date(self, post: Post, date: datetime) -> None: pass

    @abstractmethod
    def change_id_discipline(self, post: Post, discipline_id: Discipline.idDiscipline) -> None: pass

    @abstractmethod
    def change_url(self, post: Post, url: str) -> None: pass

    @abstractmethod
    def delete(self, post: Post) -> None: pass
