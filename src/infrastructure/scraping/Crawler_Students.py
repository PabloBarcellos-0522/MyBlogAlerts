from src.domain.models.Student import Student
from src.infrastructure.scraping.Scraping_Login import ScrapingLogin


class CrawlerStudents:
    def __init__(self, login: ScrapingLogin):
        self.page = login

    def get_name(self, student: Student):
        name = self.page.html.find('p', class_='perfil-aluno-nome').text

        student.Name = name
        return name
