
from src.domain.models.Post import Post
from abc import ABC, abstractmethod


class PostRepository(ABC):
    @abstractmethod
    def save(self, post: Post) -> None:
        pass

    @abstractmethod
    def delete(self, post: Post) -> None:
        pass
