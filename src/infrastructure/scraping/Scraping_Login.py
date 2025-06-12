import requests
from bs4 import BeautifulSoup


class ScrapingLogin:
    def __init__(self):
        self.url = 'https://aluno.uvv.br/'
        self.url_logout = 'https://aluno.uvv.br/Aluno/Logout'
        self.url_disciplines = 'https://aluno.uvv.br/Ajax/GetSujectList/?year={}&semester={}'
        self.url_posts = 'https://aluno.uvv.br/Aluno/BlogCarregarMais/?parametros={}&pageSize=3&pageNumber={}&filter='
        self.resp = None
        self.json_data = None
        self.html = None
        self.session = requests.session()

    def login(self, registration: str, password: str):
        self.json_data = {
            "Matricula": registration,
            "password": password
        }

        self.resp = self.session.post(self.url, data=self.json_data)
        if self.resp.status_code == 200:
            self.html = BeautifulSoup(self.resp.content, 'html.parser')
        return self.html

    def logout(self):
        self.resp = self.session.get(self.url_logout)
        if self.resp.status_code == 200:
            self.html = BeautifulSoup(self.resp.content, 'html.parser')
        return self.html
