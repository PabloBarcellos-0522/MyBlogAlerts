from src.infrastructure.scraping.Scraping_Login import ScrapingLogin
from src.infrastructure.database.Student_pg import StudentDatabase, Student
from src.infrastructure.database.Student_Discipline_pg import StudentDisciplineDatabase, StudentDiscipline
import time


class SaveStudent:
    def __init__(self):
        self.page = ScrapingLogin()
        self.stu_data = StudentDatabase()
        self.stu_disc_data = StudentDisciplineDatabase()

    def new_student(self, phone: str, registration: str, password: str) -> Student | str:
        stu = Student(phone, registration, password)
        html = self.page.login(stu.Registration, stu.Password)
        error = html.find('div', class_='alert-danger')
        self.page.logout()

        if error is not None:
            print(error.text)
            return error
        print('Logado com sucesso!')

        for s in self.stu_data.get_students():
            if s[4] == stu.Registration:
                print('Usuário já cadastrado')
                return 'Usuário já cadastrado'

        self.stu_data.save(stu)
        return stu

    def del_student(self, regisration: str):
        stu = None
        for s in self.stu_data.get_students():
            if s[4] == regisration:
                stu = Student(s[1], s[4], s[2], s[0], s[3])

        stu_disc = []
        for s in self.stu_disc_data.get_this_student(stu.Id_Student):
            stu_disc.append(StudentDiscipline(s[0], s[1]))

        for i in stu_disc:
            self.stu_disc_data.delete(i)
            time.sleep(1)
        self.stu_data.delete(stu)
