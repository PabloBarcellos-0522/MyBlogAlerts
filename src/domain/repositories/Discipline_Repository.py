from typing import List
from src.domain.models.Discipline import Discipline
from abc import ABC, abstractmethod


class DisciplineRepository(ABC):
    @abstractmethod
    def save(self, discipline: Discipline) -> None: pass

    @abstractmethod
    def get_disciplines(self) -> List[tuple]: pass

    @abstractmethod
    def chage_name(self, discipline: Discipline, new_name: str) -> None: pass

    @abstractmethod
    def chage_id_cripto(self, discipline: Discipline, new_id: str) -> None: pass

    @abstractmethod
    def delete(self, discipline: Discipline) -> None: pass
