from src.domain.models.Student import Student
from src.infrastructure.scraping.Scraping_Login import ScrapingLogin
from bs4 import BeautifulSoup


class CrawlerStudents:
    def __init__(self):
        self.page = ScrapingLogin()

    def get_name(self, student: Student):
        self.page.login(student.Registration, student.Password)
        name = self.page.html.find('p', class_='perfil-aluno-nome').text

        student.Name = name
        return name
