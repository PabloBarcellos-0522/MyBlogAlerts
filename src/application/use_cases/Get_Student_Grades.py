from src.domain.services.Scraping_Service import ScrapingService
from src.domain.repositories.Student_Repository import StudentRepository


class GetStudentGrades:
    def __init__(self, scraping_service: ScrapingService, student_repository: StudentRepository):
        self.scraping_service = scraping_service
        self.student_repository = student_repository

    def execute(self, phone_number: str) -> str:
        """
        Executes the use case to get grades for a student identified by their phone number.
        """
        # 1. Find the student by their phone number using the repository
        student = self.student_repository.get_by_phone_number(phone_number)

        # 2. Check if the student was found
        if not student:
            return "Você não está cadastrado no MyBlogAlerts. Entre em contato com o responsável para se cadastrar."

        # 3. If the student exists, get credentials and call the scraping service
        registration = student.registration
        password = student.password  # The password must be available and decrypted here

        grades_data = self.scraping_service.get_grades(registration, password)

        if not grades_data:
            return f"Nenhuma nota encontrada para a matrícula {registration} no momento."

        # 4. Format the success response
        response_message = f"Notas para o aluno {student.name}:\n\n"
        for discipline, grades_dict in grades_data.items():
            av1 = grades_dict.get('AV1') or '-'
            av2 = grades_dict.get('AV2') or '-'
            mp = grades_dict.get('MP') or '-'
            final = grades_dict.get('FINAL') or '-'
            
            grades_str = f"AV1: {av1}, AV2: {av2}, MP: {mp}, Final: {final}"
            response_message += f"- *{discipline}*: {grades_str}\n"

        return response_message
