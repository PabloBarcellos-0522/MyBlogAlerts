import datetime
from bs4 import BeautifulSoup
from requests import Response
from src.domain.models.Post import Post
from src.domain.models.Discipline import Discipline
import locale


class Utils:
    @staticmethod
    def catch_year_semester():
        current_date = datetime.date.today()
        year = current_date.year
        month = current_date.month

        if 1 <= month <= 6:
            semester = 1
        else:
            semester = 2

        return year, semester

    @staticmethod
    def contructor_desciplines(data: Response):
        disciplines = []
        for i in data.json():
            disc_name = i['NomeDisciplina']
            disc_name = str(disc_name).replace('\t', '')
            disc_id = i['IdBlogPostCripto']

            new_discipline = Discipline(Name=disc_name, Id_Cipto=disc_id)
            disciplines.append(new_discipline)
        return disciplines

    @staticmethod
    def get_frist_id(body):
        posts = []
        for card in body.find_all('div', class_='card-turma'):
            if card.find('a').get('href') == "#":
                url_id = card.find('a').find_next('a').get('href').split('=')[1]
                posts.append(url_id)
            else:
                url_id = card.find('a').get('href').split('=')[1]
                posts.append(url_id)
        return posts[0]

    @staticmethod
    def catch_posts(body: BeautifulSoup, discipline: Discipline):
        posts_list = []

        for i in body.find_all('li', class_='timeline-inverted'):
            date = i.find('div', class_='timeline-date').text
            locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
            format_date = '%d %b %Y'
            date += ' ' + str(datetime.date.today().year)
            date = datetime.datetime.strptime(date, format_date)

            title = i.find(class_='panel-title').text
            title = title.replace("'", "''").replace('"', '""')
            url = 'https://aluno.uvv.br' + i.find('a', class_='btn')['href']

            panel_body = i.find('div', class_='panel-body')

            # Remover elementos indesejados
            for unwanted in panel_body.find_all(['a', 'script', 'style']):
                unwanted.decompose()

            # Função auxiliar para extrair texto recursivamente
            def extract_text(element):
                texts = []
                for child in element.children:
                    if child.name == 'br':
                        texts.append('\n')
                    elif child.name is None:  # Text node
                        text = child.strip()
                        if text:
                            texts.append(text)
                    else:
                        texts.append(extract_text(child))
                return ' '.join(texts)

            raw_text = extract_text(panel_body)

            msg = raw_text.replace(' .', '.').replace(' ,', ',')
            msg = '\n'.join(line.strip() for line in msg.split('\n') if line.strip())

            txt = f"{title}:\n{msg}"
            txt = txt.replace("'", "''").replace('"', '""')

            new_post = Post(date, url, discipline.idDiscipline, txt)
            posts_list.append(new_post)

        return posts_list
