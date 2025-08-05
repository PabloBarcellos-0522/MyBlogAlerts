from typing import List
from bs4 import BeautifulSoup
from src.domain.models import Post
from src.domain.models.Discipline import Discipline
from src.infrastructure.scraping.Scraping_Login import ScrapingLogin
from src.infrastructure.scraping.Utils import Utils
import requests


class CrawlerPosts:
    def __init__(self, login: ScrapingLogin):
        self.page = login

    def get_posts(self, discipline: Discipline) -> List[Post]:
        try:
            page = 0
            post_list = []
            while True:
                resp = self.page.session.get(self.page.url_posts.format(discipline.Id_Cipto, page), timeout=3)
                if (not resp.text.strip()) or page >= 3:
                    break

                html = BeautifulSoup(resp.content, 'html.parser')
                posts = Utils.catch_posts(html, discipline)
                post_list.append(posts)
                page += 1
            unique_list = [post for sub in post_list for post in sub]
            return unique_list
        except requests.exceptions.RequestException as e:
            print(f"Erro de rede: {e}\n\nSeguindo programa. . .")
            return []
