from typing import List, Optional, Dict
from src.domain.models.Discipline import Discipline
from src.domain.models.Post import Post
from src.domain.services.Scraping_Service import ScrapingService
from src.infrastructure.scraping.Crawler_Students import CrawlerStudents
from src.infrastructure.scraping.Scraping_Login import ScrapingLogin
from src.infrastructure.scraping.Crawler_Disciplines import CrawlerDisciplines
from src.infrastructure.scraping.Crawler_Posts import CrawlerPosts
from src.infrastructure.scraping.Crawler_Grades import CrawlerGrades
from bs4 import BeautifulSoup


class ScrapingAdapter(ScrapingService):
    """
    Adapter that wraps the original scraping classes and implements the ScrapingService interface.
    """
    def __init__(self):
        self.page_handler = ScrapingLogin()
        self.student_crawler = CrawlerStudents(self.page_handler)
        self.discipline_crawler = CrawlerDisciplines(self.page_handler)
        self.post_crawler = CrawlerPosts(self.page_handler)
        self.grades_crawler = CrawlerGrades(self.page_handler)

    def get_grades(self, registration: str, password: str) -> Dict[str, Dict[str, str]]:
        print(f"ScrapingAdapter: Fetching grades for {registration}.")
        return self.grades_crawler.fetch_grades(registration, password)

    def get_student_name(self, registration: str, password: str) -> str:
        self.page_handler.login(registration, password)
        return self.student_crawler.get_name()

    def login(self, registration: str, password: str) -> Optional[BeautifulSoup]:
        return self.page_handler.login(registration, password)

    def logout(self) -> None:
        self.page_handler.logout()

    def get_disciplines(self) -> Optional[List[Discipline]]:
        return self.discipline_crawler.get_disciplines()

    def get_posts(self, discipline: Discipline) -> Optional[List[Post]]:
        return self.post_crawler.get_posts(discipline)
