import time
from typing import List
from bs4 import BeautifulSoup
from src.domain.models import Post
from src.domain.models.Discipline import Discipline
from src.infrastructure.scraping.Scraping_Login import ScrapingLogin
from src.infrastructure.scraping.Utils import Utils
import requests


# Constants for retry logic
MAX_PAGES_TO_SCRAPE = 50
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 5
REQUEST_TIMEOUT_SECONDS = 10


class CrawlerPosts:
    def __init__(self, login: ScrapingLogin):
        self.page = login

    def get_posts(self, session: requests.Session, discipline: Discipline) -> List[Post]:
        time.sleep(1)  # Be nice to the server before starting
        all_posts = []
        page = 0
        
        while page < MAX_PAGES_TO_SCRAPE:
            resp = self._fetch_page_with_retries(session, discipline.id_cripto, page)

            if resp is None:
                break

            if not resp.text.strip():
                break

            html = BeautifulSoup(resp.content, 'html.parser')
            posts = Utils.catch_posts(html, discipline)

            if not posts:
                break

            all_posts.extend(posts)
            page += 1

        return all_posts

    def _fetch_page_with_retries(self, session: requests.Session, discipline_id: str, page: int) -> requests.Response | None:
        for attempt in range(MAX_RETRIES):
            try:
                resp = session.get(
                    self.page.url_posts.format(discipline_id, page),
                    timeout=REQUEST_TIMEOUT_SECONDS
                )
                resp.raise_for_status()
                return resp
            except requests.exceptions.RequestException as e:
                print(f"Erro de rede ao buscar posts (tentativa {attempt + 1}/{MAX_RETRIES}): {e}")
                if attempt < MAX_RETRIES - 1:
                    time.sleep(RETRY_DELAY_SECONDS)
        
        print(f"Máximo de tentativas atingido para a página {page}. Desistindo da disciplina atual.")
        return None
