from .Student import StudentModel


class Students:
    def __init__(self, api_call):
        self.api_call = api_call

    def get_student_ids(self):
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

    def get_students(self) -> list[StudentModel]:
        """Returns a list of students using the StudentModel"""
        r = self.api_call("students")
        students = []
        for student in r["users"]:
            students.append(StudentModel(**student))
        return students

    def get_schools(self):
        """Returns a list of schools"""
        r = self.api_call("schools")
        return r

    def get_school(self, pid):
        """Returns information about a school using it's SourcedID"""
        r = self.api_call(f"schools/{pid}")
        return r

    def get_school_students(self, pid):
        """Returns a list of Students by School SourcedID"""
        r = self.api_call(f"schools/{pid}/students")
        return r

    def get_class(self, sourcedId):
        r = self.api_call(f"classes/{sourcedId}")
        return r
