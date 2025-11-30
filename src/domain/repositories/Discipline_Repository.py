from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.Discipline import Discipline


class DisciplineRepository(ABC):
    @abstractmethod
    def get_all(self) -> Optional[List[Discipline]]:
        """
        Returns all disciplines from the database.
        :return: A list of Discipline objects or None if no disciplines are found.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, discipline_id: int) -> Optional[Discipline]:
        """
        Returns a discipline by its ID.
        :param discipline_id: The ID of the discipline.
        :return: A Discipline object or None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def find_by_name_and_id_cripto(self, name: str, id_cripto: str) -> Optional[Discipline]:
        """
        Finds a discipline by its name and encrypted ID.
        :param name: The name of the discipline.
        :param id_cripto: The encrypted ID of the discipline.
        :return: A Discipline object or None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def save(self, discipline: Discipline) -> Discipline:
        """
        Saves a new discipline to the database and returns it with the new ID.
        :param discipline: The Discipline object to save.
        :return: The saved Discipline object with its database ID.
        """
        raise NotImplementedError