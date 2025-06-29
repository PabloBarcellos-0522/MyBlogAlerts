import time
from typing import List
from src.domain.models.Discipline import Discipline
from src.infrastructure.scraping.Scraping_Login import ScrapingLogin
from src.infrastructure.scraping.Utils import Utils


class CrawlerDisciplines:
    def __init__(self, login: ScrapingLogin):
        self.page = login

    def get_disciplines(self) -> List[Discipline]:
        discipline_id = Utils.get_frist_id(self.page.html)
        self.page.session.get(self.page.url_posts.format(discipline_id, 0))
        year, semester = Utils.catch_year_semester()
        self.page.session.get(self.page.url_disciplines.format(year, semester))
        time.sleep(3)


        disciplines_data = self.page.session.get(self.page.url_disciplines.format(year, semester), timeout=3)
        disciplines = Utils.contructor_desciplines(disciplines_data)
        return disciplines
