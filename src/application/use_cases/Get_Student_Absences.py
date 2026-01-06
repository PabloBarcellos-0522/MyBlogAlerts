from src.domain.services.Scraping_Service import ScrapingService
from src.domain.repositories.Student_Repository import StudentRepository


class GetStudentAbsences:
    def __init__(self, scraping_service: ScrapingService, student_repository: StudentRepository):
        self.scraping_service = scraping_service
        self.student_repository = student_repository

    def execute(self, phone_number: str) -> str:
        """
        Executes the use case to get absences for a student identified by their phone number.
        """
        student = self.student_repository.get_by_phone_number(phone_number)

        if not student:
            return "Você não está cadastrado no MyBlogAlerts. Entre em contato com o responsável para se cadastrar."

        registration = student.registration
        password = student.password

        absences_data = self.scraping_service.get_absences(registration, password)

        if not absences_data:
            return f"Nenhuma falta encontrada para a matrícula {registration} no momento."

        response_message = f"Faltas para o aluno {student.name}:\n\n"
        for discipline, absences_dict in absences_data.items():
            response_message += f"{discipline}\n"

            tf1 = absences_dict.get('TF1') or '-'
            tf2 = absences_dict.get('TF2') or '-'
            tf = absences_dict.get('TF') or '-'
            resultado = absences_dict.get('RESULTADO') or '-'

            response_message += f"- TF1: *{tf1}*\n"
            response_message += f"- TF2: *{tf2}*\n"
            response_message += f"- TF: *{tf}*\n"
            response_message += f"- Resultado: *{resultado}*\n\n"

        return response_message
