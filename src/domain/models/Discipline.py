from dataclasses import dataclass
from typing import Optional


@dataclass
class Discipline:
    Name: str
    Id_Cipto: str
    idDiscipline: Optional[int] = None
