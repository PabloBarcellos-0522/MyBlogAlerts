from typing import List, Optional, Dict
from src.domain.models.Discipline import Discipline
from src.domain.models.Post import Post
from src.domain.models.Student import Student
from src.domain.models.Student_Discipline import StudentDiscipline
from src.domain.repositories.Discipline_Repository import DisciplineRepository
from src.domain.repositories.Post_Repository import PostRepository
from src.domain.repositories.Student_Discipline_Repository import StudentDisciplineRepository
from src.domain.repositories.Student_Repository import StudentRepository


class InMemoryStore:
    """
    Acts as a central in-memory cache for database entities
    to minimize database read operations.
    """

    def __init__(self):
        self.students: List[Student] = []
        self._students_by_phone: Dict[str, Student] = {}  # Index for fast lookups
        self.disciplines: List[Discipline] = []
        self.posts: List[Post] = []
        self.student_disciplines: List[StudentDiscipline] = []

    def get_student_by_phone(self, phone_number: str) -> Optional[Student]:
        """Gets a student by phone number from the in-memory cache."""
        return self._students_by_phone.get(phone_number)

    def get_discipline_by_id(self, discipline_id: int) -> Optional[Discipline]:
        for discipline in self.disciplines:
            if discipline.id_discipline == discipline_id:
                return discipline
        return None

    def add_discipline(self, discipline: Discipline):
        if discipline not in self.disciplines:
            self.disciplines.append(discipline)

    def add_post(self, post: Post):
        if post not in self.posts:
            self.posts.append(post)

    def add_student_discipline_association(self, association: StudentDiscipline):
        if association not in self.student_disciplines:
            self.student_disciplines.append(association)

    def full_sync(self,
                  student_repo: StudentRepository,
                  discipline_repo: DisciplineRepository,
                  post_repo: PostRepository,
                  student_discipline_repo: StudentDisciplineRepository):
        """
        Loads all data from the database into the in-memory store.
        This is an expensive operation and should be called sparingly.
        """
        print("Performing full data synchronization with the database...")
        try:
            self.students = student_repo.get_all()
            self._students_by_phone = {student.phone_number: student for student in self.students}
            print(f"  {len(self.students or [])} students loaded and indexed by phone.")

            self.disciplines = discipline_repo.get_all()
            print(f"  {len(self.disciplines or [])} disciplines loaded.")

            self.posts = post_repo.get_all()
            print(f"  {len(self.posts or [])} posts loaded.")
            
            self.student_disciplines = student_discipline_repo.get_all() or []
            print(f"  {len(self.student_disciplines or [])} associations loaded.")

            print("Full synchronization complete.")
        except Exception as e:
            print(f"An error occurred during full synchronization: {e}")
