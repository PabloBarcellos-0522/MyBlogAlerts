from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.Discipline import Discipline
from src.domain.models.Post import Post


class ScrapingService(ABC):
    @abstractmethod
    def login(self, registration: str, password: str) -> None:
        """
        Logs into the academic portal.
        :param registration: The student's registration number.
        :param password: The student's password.
        """
        raise NotImplementedError

    @abstractmethod
    def logout(self) -> None:
        """ Logs out of the academic portal. """
        raise NotImplementedError

    @abstractmethod
    def get_disciplines(self) -> Optional[List[Discipline]]:
        """
        Scrapes and returns the list of disciplines for the logged-in student.
        :return: A list of Discipline objects.
        """
        raise NotImplementedError

    @abstractmethod
    def get_posts(self, discipline: Discipline) -> Optional[List[Post]]:
        """
        Scrapes and returns the list of posts for a given discipline.
        :param discipline: The Discipline object to scrape posts from.
        :return: A list of Post objects.
        """
        raise NotImplementedError

    @abstractmethod
    def get_student_name(self, registration: str, password: str) -> str:
        raise NotImplementedError
