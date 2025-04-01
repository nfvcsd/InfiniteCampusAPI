from pydantic import BaseModel, UUID4, PositiveInt
from datetime import datetime


class StudentModel(BaseModel):
    sourcedId: UUID4
    status: str
    dateLastModified: datetime
    username: PositiveInt
    enabledUser: bool
    givenName: str
    familyName: str
    metadata: dict


class Student:

    def __init__(self, api_call):
        self.api_call = api_call

    def get_student(self, pid: UUID4) -> StudentModel:
        r = self.api_call(f"students/{pid}")
        return StudentModel(**r["user"])

    def get_student_classes(self, pid: UUID4):
        r = self.api_call(f"students/{pid}/classes")
        return r
