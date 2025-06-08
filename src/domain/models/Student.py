from dataclasses import dataclass
from typing import Optional


@dataclass
class Student:
    Phone_Number: str
    Registration: str
    Password: str
    Id_Student: Optional[int] = None
    Name: Optional[str] = None
