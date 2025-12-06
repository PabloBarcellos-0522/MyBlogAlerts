import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os


class ScrapingLogin:
    def __init__(self):
        load_dotenv()
        self.url = os.getenv('BLOG_URL')
        self.url_logout = self.url + '/Aluno/Logout'
        self.url_disciplines = self.url + '/Ajax/GetSujectList/?year={}&semester={}'
        self.url_posts = self.url + '/Aluno/BlogCarregarMais/?parametros={}&pageSize=3&pageNumber={}&filter='
        self.resp = None
        self.json_data = None
        self.html = None
        self.session = requests.session()
        self.max_attempts = 3
        self.recovery_attempts = 1

    def login(self, registration: str, password: str):
        self.recovery_attempts = 1
        self.json_data = {
            "Matricula": registration,
            "password": password
        }
        while not self.recovery_attempts > self.max_attempts:
            time.sleep(1)
            try:
                self.resp = self.session.post(self.url, data=self.json_data)
                if self.resp.status_code == 200:
                    self.html = BeautifulSoup(self.resp.content, 'html.parser')
                    return self.session, self.html
                else:
                    print(f"Erro ao tentar fazer login tentativa {self.recovery_attempts}/{self.max_attempts}")
                    self.recovery_attempts += 1
            except requests.exceptions.RequestException as e:
                print(f"Erro de rede: {e}\n\nSeguindo programa. . .")
                print(f"Erro ao tentar fazer login tentativa {self.recovery_attempts}/{self.max_attempts}")
                self.recovery_attempts += 1

        print("Número máximo de tentativas de login atingido. Falha no login.")
        return None, None

    def logout(self):
        try:
            self.resp = self.session.get(self.url_logout)
            if self.resp.status_code == 200:
                self.html = BeautifulSoup(self.resp.content, 'html.parser')
            return self.html
        except requests.exceptions.RequestException as e:
            print(f"Erro de rede: {e}\n\nSeguindo programa. . .")
            return None
