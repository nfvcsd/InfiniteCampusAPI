from .Student import StudentModel
from pydantic import UUID4
from .Classes import ClassesModel


class Students:
    def __init__(self, api_call):
        self.api_call = api_call

    def get_student_ids(self):
        """Returns Student name and SourcedID with minimum of 4 digits"""
        data = []
        r = self.api_call("students")
        for user in r["users"]:
            sourcedid = user["sourcedId"]
            name = f"{user['givenName']} {user['familyName']}"
            if sourcedid[0] == "s":
                sourcedid = f"{sourcedid[1:]}"
            sourcedid = int(sourcedid)
            data.append({"name": name, "ID": f"{sourcedid:04}"})
        return data

    def get_students(self, filters: str = "") -> list[StudentModel]:
        """Returns a list of students using the StudentModel"""
        r = self.api_call("students", filters=filters)
        students = []
        for student in r["users"]:
            students.append(StudentModel(**student))
        return students

    def get_class(self, sourcedId: UUID4) -> ClassesModel:
        """I can't test this because it requires a vendor license"""
        r = self.api_call(f"classes/{sourcedId}")
        return ClassesModel(**r)
