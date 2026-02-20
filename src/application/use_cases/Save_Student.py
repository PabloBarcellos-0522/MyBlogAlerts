from src.domain.repositories.Student_Repository import StudentRepository
from src.domain.repositories.Student_Discipline_Repository import StudentDisciplineRepository
from src.domain.services.Scraping_Service import ScrapingService
from src.domain.models.Student import Student
from typing import Union


class StudentCreationError(Exception):
    """Exceção para falhas durante a criação do aluno após o salvamento."""
    pass


class SaveStudent:
    def __init__(self, student_repo: StudentRepository, student_discipline_repo: StudentDisciplineRepository,
                 scraping_service: ScrapingService):
        self.student_repo = student_repo
        self.student_discipline_repo = student_discipline_repo
        self.scraping_service = scraping_service

    def new_student(self, phone: str, faculty_registration: str, password: str) -> Union[Student, str]:
        try:
            # 1. Verificar se o aluno já existe (agora busca no cache e no banco)
            if self.student_repo.find_by_registration(faculty_registration):
                return f"Aluno com matrícula {faculty_registration} já existe."

            # 2. Validar credenciais via login, tratando o erro específico de scraping
            name = None
            try:
                name = self.scraping_service.get_student_name(faculty_registration, password)
            except AttributeError as e:
                # Este erro ('NoneType' object has no attribute 'text') acontece quando o login falha.
                # Capturamos e tratamos como uma falha de login esperada, deixando o 'name' como None.
                print(f"AttributeError durante o scraping (esperado em login falho): {e}")
                pass

            if not name:
                return "Falha na validação das credenciais. Verifique a matrícula e a senha."

            # 3. Criar e salvar o aluno (o repositório agora retorna o objeto com ID e atualiza o cache)
            student_to_save = Student(
                name=name,
                phone_number=phone,
                registration=faculty_registration,
                password=password
            )
            saved_student = self.student_repo.save(student_to_save)

            return saved_student

        except Exception as e:
            print(f"Erro inesperado no método new_student: {e}")
            raise  # Propaga a exceção para a API tratar como um erro 500

    def del_student(self, faculty_registration: str, password: str) -> Union[bool, str]:
        try:
            # Primeiro, valida as credenciais para autorizar a exclusão
            try:
                login_success = self.scraping_service.get_student_name(faculty_registration, password)
            except AttributeError:
                login_success = False

            if not login_success:
                return "Falha na validação das credenciais. Matrícula ou senha incorretas."

            # Se o login for bem-sucedido, busca o aluno para obter o ID
            student_to_delete = self.student_repo.find_by_registration(faculty_registration)
            if not student_to_delete or not student_to_delete.id_student:
                # Este caso é raro, pois o login funcionou, mas o aluno não está no banco.
                return "Aluno não encontrado no banco de dados, embora o login tenha funcionado."

            # Prossiga com a exclusão
            self.student_discipline_repo.delete_by_student_id(student_to_delete.id_student)
            print(f"Associações de disciplina para o aluno ID {student_to_delete.id_student} foram deletadas.")

            self.student_repo.delete(student_to_delete.id_student)
            print(f"Aluno com ID {student_to_delete.id_student} foi deletado.")

            return True
        except Exception as e:
            print(f"Ocorreu um erro ao deletar o aluno {faculty_registration}: {e}")
            return "Ocorreu um erro inesperado durante a exclusão do aluno."
