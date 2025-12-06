from src.domain.repositories.Student_Repository import StudentRepository
from src.domain.repositories.Student_Discipline_Repository import StudentDisciplineRepository
from src.domain.services.Scraping_Service import ScrapingService
from src.domain.models.Student import Student
from typing import Union


class SaveStudent:
    def __init__(self, student_repo: StudentRepository, student_discipline_repo: StudentDisciplineRepository,
                 scraping_service: ScrapingService):
        self.student_repo = student_repo
        self.student_discipline_repo = student_discipline_repo
        self.scraping_service = scraping_service

    def new_student(self, name: str, phone: str, faculty_registration: str, password: str) -> Union[Student, str]:
        try:
            existing_student = self.student_repo.find_by_registration(faculty_registration)
            if existing_student:
                return f"Student with registration {faculty_registration} already exists."

            student = Student(
                name=name,
                phone_number=phone,
                registration=faculty_registration,
                password=password
            )
            self.student_repo.save(student)

            newly_saved_student = self.student_repo.find_by_registration(faculty_registration)
            if not newly_saved_student:
                return "Failed to save and retrieve the new student."

            return newly_saved_student
        except Exception as e:
            return f"An unexpected error occurred: {e}"

    def del_student(self, faculty_registration: str) -> bool:
        try:
            student_to_delete = self.student_repo.find_by_registration(faculty_registration)
            if not student_to_delete or not student_to_delete.id_student:
                print(f"Student with registration {faculty_registration} not found.")
                return False

            # First, delete associations
            self.student_discipline_repo.delete_by_student_id(student_to_delete.id_student)
            print(f"Deleted discipline associations for student ID {student_to_delete.id_student}.")

            # Then, delete the student
            self.student_repo.delete(student_to_delete.id_student)
            print(f"Deleted student with ID {student_to_delete.id_student}.")

            return True
        except Exception as e:
            print(f"An error occurred while deleting student {faculty_registration}: {e}")
            return False
