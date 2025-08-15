import time
from src.infrastructure.database.Post_pg import PostDatabase, Post
from src.infrastructure.database.Discipline_pg import DisciplineDatabase, Discipline
from src.infrastructure.database.Student_pg import StudentDatabase, Student
from src.infrastructure.database.Student_Discipline_pg import StudentDisciplineDatabase, StudentDiscipline
from src.infrastructure.scraping.Scraping_Login import ScrapingLogin
from src.infrastructure.scraping.Crawler_Posts import CrawlerPosts
from src.infrastructure.scraping.Crawler_Disciplines import CrawlerDisciplines
from src.application.services.Send_Whatsapp_Msg import SendMensage


class SavePost:
    def __init__(self):
        self.send = SendMensage()
        self.posts = PostDatabase()
        self.disciplines = DisciplineDatabase()
        self.students = StudentDatabase()
        self.students_disciplines = StudentDisciplineDatabase()
        self.saved_posts = []
        self.saved_disciplines = []
        self.saved_students = []
        self.saved_students_disciplines = []

        # Scraping:
        self.page = ScrapingLogin()
        self.scrap_disciplines = CrawlerDisciplines(self.page)
        self.scrap_posts = CrawlerPosts(self.page)
        self.scr_student_disciplines = {}
        self.scr_discipline_posts = {}

    def update_all_memory(self):
        print("update_all_memory")
        self.update_posts()
        self.update_disciplines()
        self.update_students()
        self.update_students_disciplines()

    def update_posts(self):
        print('update_posts')

        list_posts = []
        for post in self.posts.get_posts():
            id_p = post[0]
            date = post[1]
            url = post[2]
            discipline_id = post[3]
            content = post[4]

            list_posts.append(Post(date, url, discipline_id, content, id_p))
        self.saved_posts = list_posts

    def update_disciplines(self):
        print('update_disciplines')

        list_disc = []
        for disc in self.disciplines.get_disciplines():
            id_d = disc[0]
            name = disc[1]
            id_crip = disc[2]

            list_disc.append(Discipline(name, id_crip, id_d))
        self.saved_disciplines = list_disc

    def update_students(self):
        print('update_students')

        list_students = []
        for stu in self.students.get_students():
            id_s = stu[0]
            phone = stu[1]
            password = stu[2]
            name = stu[3]
            registration = stu[4]

            list_students.append(Student(phone, registration, password, id_s, name))
        self.saved_students = list_students

    def update_students_disciplines(self):
        print('update_students_disciplines')

        list_disc_posts = []
        for stu in self.students_disciplines.get_students_disciplines():
            id_s = stu[0]
            id_d = stu[1]

            list_disc_posts.append(StudentDiscipline(id_s, id_d))
        self.saved_students_disciplines = list_disc_posts

    def search_scraping_disciplines(self):
        print('search_scraping_disciplines')
        for stu in self.saved_students:
            self.page.login(stu.Registration, stu.Password)
            disc = self.scrap_disciplines.get_disciplines()
            if disc:
                self.scr_student_disciplines.update({stu.Id_Student: disc})
            self.page.logout()

        self.validate_scrap_discipline()
        time.sleep(3)
        self.update_disciplines()

    def search_scraping_posts(self):
        print('search_scraping_posts')
        for stu in self.saved_students:
            self.page.login(stu.Registration, stu.Password)
            for disc in self.saved_disciplines:
                posts = self.scrap_posts.get_posts(disc)
                self.scr_discipline_posts.update({disc.idDiscipline: posts})
            self.page.logout()

        self.validate_scrap_post()
        time.sleep(3)
        self.update_posts()

    def validate_scrap_discipline(self):
        print('validate_scrap_discipline')
        existing = []
        for student_id in self.scr_student_disciplines.keys():
            for discipline in self.scr_student_disciplines[student_id]:
                for s_discipline in self.saved_disciplines:
                    if (discipline.Name == s_discipline.Name) and (discipline.Id_Cipto == s_discipline.Id_Cipto) and discipline.Id_Cipto is not None:
                        existing.append(discipline)
                        stu_disc = StudentDiscipline(student_id, s_discipline.idDiscipline)
                        for i in self.saved_students_disciplines:
                            if (i.Id_Student == stu_disc.Id_Student) and (i.Id_Discipline == stu_disc.Id_Discipline):
                                break
                        else:
                            self.students_disciplines.save(stu_disc)
                            self.saved_students_disciplines.append(stu_disc)
        for key in self.scr_student_disciplines.keys():
            for disc in existing:
                if disc in self.scr_student_disciplines[key]:
                    self.scr_student_disciplines[key].remove(disc)
        for key in self.scr_student_disciplines.keys():
            for discipline in self.scr_student_disciplines[key]:
                if discipline.Id_Cipto is not None:
                    self.disciplines.save(discipline)

    def validate_scrap_post(self):
        print('validate_scrap_post')
        existing = []
        for disc_id in self.scr_discipline_posts.keys():
            for post in self.scr_discipline_posts[disc_id]:
                for s_post in self.saved_posts:
                    day = post.Post_date.day == s_post.Post_date.day
                    month = post.Post_date.month == s_post.Post_date.month
                    year = post.Post_date.year == s_post.Post_date.year

                    if day and month and year and (post.Post_Url == s_post.Post_Url) and (post.Discipline_id == s_post.Discipline_id):
                        existing.append(post)
                        break
        for key in self.scr_discipline_posts.keys():
            for post in existing:
                if post in self.scr_discipline_posts[key]:
                    self.scr_discipline_posts[key].remove(post)
        for key in self.scr_discipline_posts.keys():
            for post in reversed(self.scr_discipline_posts[key]):
                print("Send new post...")
                disc_name = None
                for disc in self.saved_disciplines:
                    if disc.idDiscipline == key:
                        disc_name = disc.Name
                print(self.send.group_msg(disc_name + ":\n" + post.Content + '\nUrl: ' + post.Post_Url))
                time.sleep(0.5)
                self.posts.save(post)
