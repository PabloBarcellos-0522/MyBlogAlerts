from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.models.Post import Post
from datetime import date


class PostRepository(ABC):
    @abstractmethod
    def save(self, post: Post) -> None:
        """
        Saves a new post to the database.
        :param post: The Post object to save.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_url_and_date(self, url: str, post_date: date) -> Optional[Post]:
        """
        Finds a post by its URL and publication date.
        :param url: The URL of the post.
        :param post_date: The publication date of the post.
        :return: A Post object or None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> Optional[List[Post]]:
        """
        Returns all posts from the database.
        :return: A list of Post objects or None if no posts are found.
        """
        raise NotImplementedError