from bs4 import BeautifulSoup
from src.domain.models.Discipline import Discipline
from src.infrastructure.scraping.Scraping_Login import ScrapingLogin
from src.infrastructure.scraping.Utils import Utils


class CrawlerPosts:
    def __init__(self):
        self.page = ScrapingLogin()

    def get_posts(self, registration: str, password: str, discipline: Discipline):
        self.page.login(registration, password)

        page = 0
        post_list = []
        while True:
            resp = self.page.session.get(self.page.url_posts.format(discipline.Id_Cipto, page))
            if not resp.text.strip():
                break

            html = BeautifulSoup(resp.content, 'html.parser')
            posts = Utils.catch_posts(html, discipline)
            post_list.append(posts)
            page += 1
        unique_list = [post for sub in post_list for post in sub]
        return unique_list
