from typing import List
from src.domain.models.Discipline import Discipline
from src.infrastructure.scraping.Scraping_Login import ScrapingLogin
from src.infrastructure.scraping.Utils import Utils
import requests


class CrawlerDisciplines:
    def __init__(self, login: ScrapingLogin):
        self.page = login

    def get_disciplines(self) -> List[Discipline]:
        try:
            disciplines = []
            discipline_id = Utils.get_first_id(self.page.html)
            if discipline_id:
                # This first request seems to be necessary to initialize the server-side session
                self.page.session.get(self.page.url_posts.format(discipline_id, 0))
                year, semester = Utils.catch_year_semester()
                
                # Directly call for the disciplines data once.
                disciplines_data = self.page.session.get(self.page.url_disciplines.format(year, semester), timeout=5)
                disciplines = Utils.constructor_disciplines(disciplines_data)
            return disciplines

        except requests.exceptions.RequestException as e:
            print(f"Erro de rede: {e}\n\nSeguindo programa. . .")
            return []
