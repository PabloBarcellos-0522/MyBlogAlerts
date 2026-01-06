from abc import ABC, abstractmethod
import requests
from typing import List, Optional, Tuple, Dict
from src.domain.models.Discipline import Discipline
from src.domain.models.Post import Post
from bs4 import BeautifulSoup


class ScrapingService(ABC):
    @abstractmethod
    def login(self, registration: str, password: str) -> Optional[Tuple[requests.Session, BeautifulSoup]]:
        """
        Logs into the academic portal.
        :param registration: The student's registration number.
        :param password: The student's password.
        :return: A tuple containing the authenticated requests session and the BeautifulSoup object of the dashboard page, or None if login fails.
        """
        raise NotImplementedError

    @abstractmethod
    def logout(self) -> None:
        """ Logs out of the academic portal. """
        raise NotImplementedError

    @abstractmethod
    def get_disciplines(self, session: requests.Session, dashboard_html: BeautifulSoup) -> List[Discipline]:
        """
        Scrapes and returns the list of disciplines for the logged-in student.
        :param session: The authenticated requests session.
        :param dashboard_html: The BeautifulSoup object of the dashboard page.
        :return: A list of Discipline objects.
        """
        raise NotImplementedError

    @abstractmethod
    def get_posts(self, session: requests.Session, discipline: Discipline) -> List[Post]:
        """
        Scrapes and returns the list of posts for a given discipline.
        :param session: The authenticated requests session.
        :param discipline: The Discipline object to scrape posts from.
        :return: A list of Post objects.
        """
        raise NotImplementedError

    @abstractmethod
    def get_student_name(self, registration: str, password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_grades(self, username: str, password: str) -> Dict[str, Dict[str, str]]:
        """
        Scrapes and returns the grades for a student.
        :param username: The student's username/registration.
        :param password: The student's password.
        :return: A dictionary where keys are discipline names and values are lists of grades.
        """
        raise NotImplementedError

    @abstractmethod
    def get_absences(self, username: str, password: str) -> Dict[str, Dict[str, str]]:
        """
        Scrapes and returns the absences for a student.
        :param username: The student's username/registration.
        :param password: The student's password.
        :return: A dictionary where keys are discipline names and values are dicts of absences.
        """
        raise NotImplementedError
