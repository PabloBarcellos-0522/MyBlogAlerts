
from src.domain.models.Discipline import Discipline
from abc import ABC, abstractmethod


class DisciplineRepository(ABC):
    @abstractmethod
    def save(self, discipline: Discipline) -> None:
        pass

    @abstractmethod
    def changeid_cipto(self, discipline: Discipline, id_cripto: str) -> None:
        pass

    @abstractmethod
    def delete(self, discipline: Discipline) -> None:
        pass
