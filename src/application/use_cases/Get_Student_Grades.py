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
        student = self.student_repository.get_by_phone_number(phone_number)

        # 2. Check if the student was found
        if not student:
            return "Você não está cadastrado no MyBlogAlerts. Entre em contato com o responsável para se cadastrar."

        registration = student.registration
        password = student.password

        grades_data = self.scraping_service.get_grades(registration, password)

        if not grades_data:
            return f"Nenhuma nota encontrada para a matrícula {registration} no momento."

        response_message = f"Notas para o aluno {student.name}:\n\n"
        for discipline, grades_dict in grades_data.items():
            response_message += f"{discipline}\n"

            av1 = grades_dict.get('AV1') or '-'
            av2 = grades_dict.get('AV2') or '-'
            mp = grades_dict.get('MP') or '-'
            pf = grades_dict.get('PF') or '-'
            final = grades_dict.get('FINAL') or '-'
            resultado = grades_dict.get('RESULTADO') or '-'

            response_message += f"- AV1: *{av1}*\n"
            response_message += f"- AV2: *{av2}*\n"
            response_message += f"- MP: *{mp}*\n"
            response_message += f"- PF: *{pf}*\n"
            response_message += f"- FINAL: *{final}*\n"
            response_message += f"- Resultado: *{resultado}*\n\n"

        return response_message
