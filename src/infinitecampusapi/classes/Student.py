from pydantic import BaseModel, UUID4, PositiveInt, EmailStr
from datetime import datetime


class StudentModel(BaseModel):
    sourcedId: UUID4
    status: str
    dateLastModified: datetime
    metadata: dict
    userMasterIdentifier: PositiveInt
    identifier: PositiveInt
    username: PositiveInt
    enabledUser: bool
    phone: str = ""
    sms: str = ""
    givenName: str
    familyName: str
    middleName: str = ""
    preferredFirstName: str = ""
    preferredLastName: str = ""
    preferrredMiddleName: str = ""
    email: EmailStr | None = None
    userIds: list = []
    roles: list = []
    agents: list = []
    grades: list = []


class Student:

    def __init__(self, api_call):
        self.api_call = api_call

    def get_student(self, pid: UUID4) -> StudentModel:
        r = self.api_call(f"students/{pid}")
        return StudentModel(**r["user"])

    def get_student_classes(self, pid: UUID4):
        r = self.api_call(f"students/{pid}/classes")
        return r
