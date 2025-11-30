from src.domain.models.Student import Student
from src.domain.repositories.Student_Repository import StudentRepository
from src.domain.repositories.Student_Discipline_Repository import StudentDisciplineRepository
from src.domain.services.Scraping_Service import ScrapingService


class SaveStudent:
    """
    Use case for creating and deleting students.
    Note: This class still needs its dependencies (repositories) to be fully refactored
    to support all required operations efficiently (e.g., find_by_registration, delete).
    """

    def __init__(self,
                 student_repo: StudentRepository,
                 student_discipline_repo: StudentDisciplineRepository,
                 scraping_service: ScrapingService):
        self.student_repo = student_repo
        self.student_discipline_repo = student_discipline_repo
        self.scraping_service = scraping_service

    def new_student(self, phone: str, registration: str, password: str) -> Student | str:
        """
        Validates credentials, checks for existence, and saves a new student.
        """
        # Step 1: Validate credentials by trying to log in
        try:
            self.scraping_service.login(registration, password)
            self.scraping_service.logout()
            print('Login credentials are valid.')
        except Exception as e:
            # Assuming login service raises an exception on failure
            error_message = f"Failed to validate credentials: {e}"
            print(error_message)
            return error_message

        # Step 2: Check if student already exists
        # This requires a find_by_registration method in the repository.
        # We will assume it exists and implement it later.
        if hasattr(self.student_repo, 'find_by_registration'):
            existing_student = self.student_repo.find_by_registration(registration)
            if existing_student:
                print('Student with this registration already exists.')
                return 'Usuário já cadastrado'

        # Step 3: Save the new student
        new_stu = Student(phone_number=phone, registration=registration, password=password)
        try:
            # The save method in StudentPgRepo doesn't return the student, so we just call it
            self.student_repo.save(new_stu)
            print("Student saved successfully.")
            return new_stu
        except Exception as e:
            error_message = f"Failed to save student to database: {e}"
            print(error_message)
            return error_message

    def del_student(self, registration: str) -> bool:
        """
        Finds a student by registration and deletes them and their associations.
        """
        # Step 1: Find the student by registration
        # This also requires find_by_registration method.
        if not hasattr(self.student_repo, 'find_by_registration'):
            print("Feature not fully implemented: Missing find_by_registration in StudentRepository.")
            return False
            
        student_to_delete = self.student_repo.find_by_registration(registration)

        if not student_to_delete:
            print(f"No student found with registration: {registration}")
            return False

        student_id = student_to_delete.id_student

        try:
            # Step 2: Delete all student-discipline associations
            # Requires a delete_by_student_id method.
            if hasattr(self.student_discipline_repo, 'delete_by_student_id'):
                self.student_discipline_repo.delete_by_student_id(student_id)
                print(f"Deleted associations for student ID: {student_id}")
            else:
                print("Warning: Missing delete_by_student_id in StudentDisciplineRepository. Associations may not be deleted.")

            # Step 3: Delete the student
            # Requires delete method to accept an ID or a find_by_id and then delete.
            self.student_repo.delete(student_id)
            print(f"Deleted student with registration: {registration}")
            return True
        except Exception as e:
            print(f"An error occurred during deletion: {e}")
            return False
