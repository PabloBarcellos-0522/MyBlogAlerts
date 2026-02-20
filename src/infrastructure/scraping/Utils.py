import datetime
from bs4 import BeautifulSoup
from requests import Response
from src.domain.models.Post import Post
from src.domain.models.Discipline import Discipline
from dotenv import load_dotenv
import os


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
    def constructor_disciplines(data: Response):
        disciplines = []
        for i in data.json():
            disc_name = i['NomeDisciplina']
            disc_name = str(disc_name).replace('\t', '')
            disc_id = i['IdBlogPostCripto']

            new_discipline = Discipline(name=disc_name, id_cripto=disc_id)
            disciplines.append(new_discipline)
        return disciplines

    @staticmethod
    def get_first_id(body):
        posts = []
        for card in body.find_all('div', class_='card-turma'):
            if card.find('a').get('href') == "#":
                url_id = card.find('a').find_next('a').get('href').split('=')[1]
                posts.append(url_id)
            else:
                try:
                    url_id = card.find('a').get('href').split('=')[1]
                    posts.append(url_id)
                except IndexError:
                    print('\nDisciplina sem link encontrada!\n')

        if posts:
            return posts[0]

    @staticmethod
    def catch_posts(body: BeautifulSoup, discipline: Discipline):
        posts_list = []

        month_map = {
            'jan': 1, 'fev': 2, 'feb': 2, 'mar': 3, 'abr': 4, 'apr': 4,
            'mai': 5, 'may': 5, 'jun': 6, 'jul': 7, 'ago': 8, 'aug': 8,
            'set': 9, 'sep': 9, 'out': 10, 'oct': 10, 'nov': 11, 'dez': 12, 'dec': 12
        }

        load_dotenv()
        BLOG_URL = os.getenv('BLOG_URL')
        for i in body.find_all('li', class_='timeline-inverted'):
            date_str = i.find('div', class_='timeline-date').text.strip().lower()  # "29 nov"
            
            try:
                day_str, month_abbr = date_str.split()
                day = int(day_str)
                month = month_map[month_abbr[:3]]
                year = datetime.date.today().year 
                # Basic logic to handle posts from the previous year in January
                if month > datetime.date.today().month:
                    year -= 1
                
                date = datetime.date(year, month, day)
            except (ValueError, KeyError) as e:
                print(f"Could not parse date: '{date_str}'. Error: {e}. Skipping post.")
                continue

            title = i.find(class_='panel-title').text

            
            url = BLOG_URL + i.find('a', class_='btn')['href']

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
                        text_content = child.strip()
                        if text_content:
                            texts.append(text_content)
                    else:
                        texts.append(extract_text(child))
                return ' '.join(texts)

            raw_text = extract_text(panel_body)
            # Clean up spacing issues that might arise from extraction
            msg = raw_text.replace(' .', '.').replace(' ,', ',')
            msg = '\n'.join(line.strip() for line in msg.split('\n') if line.strip())

            full_content = f"{title}:\n{msg}"

            new_post = Post(post_date=date, post_url=url, discipline_id=discipline.id_discipline, content=full_content)
            posts_list.append(new_post)
    
        return posts_list
