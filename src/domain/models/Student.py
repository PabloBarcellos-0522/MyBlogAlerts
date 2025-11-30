from dataclasses import dataclass
from typing import Optional


@dataclass
class Student:
    phone_number: str
    registration: str
    password: str
    id_student: Optional[int] = None
    name: Optional[str] = None
