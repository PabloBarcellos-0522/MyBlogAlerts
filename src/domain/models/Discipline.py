from dataclasses import dataclass
from typing import Optional


@dataclass
class Discipline:
    name: str
    id_cripto: str
    id_discipline: Optional[int] = None
