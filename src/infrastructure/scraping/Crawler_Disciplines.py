import html
import requests
from typing import List, Optional
from urllib.parse import parse_qs, unquote_plus
from bs4 import BeautifulSoup
from src.domain.models.Discipline import Discipline
from src.infrastructure.scraping.Scraping_Login import ScrapingLogin


class CrawlerDisciplines:
    def __init__(self, login_handler: ScrapingLogin):
        self.login_handler = login_handler  # Still needed for URL base

    def get_disciplines(self, session: requests.Session, dashboard_html: BeautifulSoup) -> List[Discipline]:
        """
        Parses the dashboard HTML to extract the student's disciplines.
        """
        # No need to fetch page again, dashboard_html is provided
        return self._parse_disciplines(dashboard_html)

    def _parse_disciplines(self, soup: BeautifulSoup) -> List[Discipline]:
        """
        Parses the BeautifulSoup object to extract discipline information.
        This unified logic handles both presential and EAD disciplines.
        """
        disciplines = []
        cards = soup.find_all("div", class_="card-turma")

        for card in cards:
            # Find the discipline name, which can be in an <h3> or <span> tag
            header_tag = card.find("h3") or card.find("span", class_="h3")
            if not header_tag:
                continue

            full_name = header_tag.get_text(strip=True)
            normalized_name = html.unescape(full_name.strip())

            id_cripto = None
            # The correct ID is always in an 'a' tag with 'parametros=' in its href
            link_tags = card.find_all("a", href=True)
            for link_tag in link_tags:
                if 'parametros=' in link_tag['href']:
                    href = link_tag['href']
                    param_start = href.find('parametros=')
                    if param_start != -1:
                        param_value_raw = href[param_start + len('parametros='):]
                        # Ensure we don't grab other potential URL parameters
                        amp_index = param_value_raw.find('&')
                        if amp_index != -1:
                            id_cripto = param_value_raw[:amp_index]
                        else:
                            id_cripto = param_value_raw
                        # Found the correct link, no need to check others for this card
                        break

            if id_cripto:
                disciplines.append(Discipline(name=normalized_name, id_cripto=id_cripto))

        return disciplines
