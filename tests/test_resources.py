import unittest

from infinitecampusapi.classes.AcademicSessions import (
    AcademicSessions,
    AcademicSessionsModel,
)
from infinitecampusapi.classes.Classes import ClassGroup, ClassesModel, ScoreScales
from infinitecampusapi.classes.Courses import CourseModel, Courses
from infinitecampusapi.classes.Demographics import Demographics, DemographicsModel
from infinitecampusapi.classes.Enrollments import Enrollments, EnrollmentsModel
from infinitecampusapi.classes.GradingPeriods import GradingPeriods
from infinitecampusapi.classes.Orgs import Orgs, OrgsModel
from infinitecampusapi.classes.Schools import SchoolModel, Schools
from infinitecampusapi.classes.Student import Student, StudentModel
from infinitecampusapi.classes.Students import Students
from infinitecampusapi.classes.Teachers import TeacherModel, Teachers
from infinitecampusapi.classes.Terms import Terms
from infinitecampusapi.classes.Users import Users, UsersModel


ID = "12345678-1234-4234-8234-1234567890ab"
OTHER_ID = "22345678-1234-4234-8234-1234567890ab"
DATE = "2026-01-02T03:04:05Z"


def ref(sourced_id=ID, resource_type="org"):
    return {
        "href": f"https://example.test/{resource_type}/{sourced_id}",
        "sourcedId": sourced_id,
        "type": resource_type,
    }


def academic_session():
    return {
        "sourcedId": ID,
        "status": "active",
        "dateLastModified": DATE,
        "metadata": {},
        "title": "2026",
        "schoolYear": "2026",
        "startDate": DATE,
        "endDate": DATE,
        "children": [],
        "parent": ref(OTHER_ID, "academicSession"),
        "type": "schoolYear",
    }


def class_record():
    return {
        "sourcedId": ID,
        "status": "active",
        "dateLastModified": DATE,
        "metadata": {},
        "title": "Algebra I",
        "classType": "scheduled",
        "classCode": "ALG-1",
        "course": ref(resource_type="course"),
        "school": ref(resource_type="org"),
        "terms": [ref(resource_type="academicSession")],
    }


def student():
    return {
        "sourcedId": ID,
        "status": "active",
        "dateLastModified": DATE,
        "metadata": {},
        "userMasterIdentifier": 1001,
        "identifier": 1001,
        "username": 1001,
        "enabledUser": True,
        "givenName": "Ada",
        "familyName": "Lovelace",
        "email": "ada@example.com",
    }


def teacher():
    return {
        "sourcedId": ID,
        "status": "active",
        "dateLastModified": DATE,
        "metadata": {"ic.legacySourcedId": "t42"},
        "username": 42,
        "enabledUser": True,
        "givenName": "Grace",
        "familyName": "Hopper",
        "email": "grace@example.com",
    }


def user():
    return {
        "sourcedId": ID,
        "status": "active",
        "dateLastModified": DATE,
        "metadata": {},
        "username": 7,
        "enabledUser": True,
        "givenName": "Linus",
        "familyName": "Torvalds",
        "email": "linus@example.com",
    }


def demographic():
    return {
        "sourcedId": ID,
        "status": "active",
        "dateLastModified": DATE,
        "metadata": {},
        "birthDate": DATE,
        "sex": "unspecified",
        "americanIndianOrAlaskaNative": False,
        "asian": False,
        "blackOrAfricanAmerican": False,
        "demographicRaceTwoOrMoreRaces": False,
        "hispanicOrLatinoEthnicity": False,
        "nativeHawaiianOrOtherPacificIslander": False,
        "white": False,
    }


def enrollment():
    return {
        "sourcedId": ID,
        "status": "active",
        "dateLastModified": DATE,
        "metadata": {},
        "role": "student",
        "primary": True,
        "beginDate": DATE,
        "endDate": DATE,
        "user": ref(resource_type="user"),
        "class": ref(resource_type="class"),
        "school": ref(resource_type="org"),
    }


def course():
    return {
        "sourcedId": ID,
        "status": "active",
        "dateLastModified": DATE,
        "metadata": {},
        "title": "Algebra",
        "courseCode": "ALG",
        "subjects": ["Mathematics"],
        "subjectCodes": ["MATH"],
        "org": ref(resource_type="org"),
    }


def school():
    return {
        "sourcedId": ID,
        "status": "active",
        "dateLastModified": DATE,
        "metadata": {},
        "name": "Example School",
        "identifier": "SCH-1",
        "children": [],
        "parent": ref(OTHER_ID, "org"),
        "type": "school",
    }


class StubAPI:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, endpoint, **kwargs):
        self.calls.append((endpoint, kwargs))
        return self.responses[endpoint]


class ResourceTests(unittest.TestCase):
    def test_students_methods(self):
        id_api = StubAPI(
            {
                "students": {"users": [student() | {"sourcedId": "s0042"}]},
            }
        )
        self.assertEqual(
            Students(id_api).get_student_ids(),
            [{"name": "Ada Lovelace", "ID": "0042"}],
        )

        api = StubAPI(
            {
                "students": {"users": [student()]},
                f"classes/{ID}": class_record(),
            }
        )
        resource = Students(api)

        self.assertIsInstance(
            resource.get_students(filters="status='active'")[0], StudentModel
        )
        self.assertIsInstance(resource.get_class(ID), ClassesModel)
        self.assertEqual(api.calls[0], ("students", {"filters": "status='active'"}))

    def test_single_student_methods(self):
        api = StubAPI(
            {
                f"students/{ID}": {"user": student()},
                f"students/{ID}/classes": {"classes": [class_record()]},
                f"demographics/{ID}": {"demographics": demographic()},
            }
        )
        resource = Student(api)

        model = resource.get_student(ID)
        self.assertIsInstance(model, StudentModel)
        self.assertEqual(
            resource.get_student_classes(ID)["classes"][0]["title"], "Algebra I"
        )
        self.assertIsInstance(
            resource.get_student_demographics(model), DemographicsModel
        )

    def test_teachers_methods(self):
        api = StubAPI(
            {
                "teachers": {"users": [teacher()]},
                f"teachers/{ID}": {"user": teacher()},
                f"classes/{ID}/teachers": {"users": [teacher()]},
            }
        )
        resource = Teachers(api)

        self.assertIsInstance(resource.get_teachers()[0], TeacherModel)
        self.assertIsInstance(resource.get_teacher(ID), TeacherModel)
        self.assertEqual(
            resource.get_teacher_ids(), [{"name": "Grace Hopper", "ID": "0042"}]
        )
        self.assertEqual(resource.get_class_teacher(ID)["givenName"], "Grace")

    def test_users_methods(self):
        api = StubAPI(
            {
                "users": {"users": [user()]},
                f"users/{ID}": {"user": user()},
                f"users/{ID}/classes": {"classes": [class_record()]},
            }
        )
        resource = Users(api)

        self.assertIsInstance(resource.get_users()[0], UsersModel)
        self.assertIsInstance(resource.get_user(ID), UsersModel)
        self.assertEqual(
            resource.get_user_classes(ID)["classes"][0]["classCode"], "ALG-1"
        )

    def test_academic_sessions_methods(self):
        api = StubAPI(
            {
                "academicSessions": {"academicSessions": [academic_session()]},
                f"academicSessions/{ID}": {"academicSession": academic_session()},
            }
        )
        resource = AcademicSessions(api)

        self.assertIsInstance(
            resource.get_academic_sessions()[0], AcademicSessionsModel
        )
        self.assertIsInstance(resource.get_academic_session(ID), AcademicSessionsModel)

    def test_courses_methods(self):
        api = StubAPI(
            {
                "courses": {"courses": [course()]},
                f"courses/{ID}": {"course": course()},
                f"courses/{ID}/classes": {"classes": [class_record()]},
            }
        )
        resource = Courses(api)

        self.assertIsInstance(resource.get_courses()[0], CourseModel)
        self.assertIsInstance(resource.get_course(ID), CourseModel)
        self.assertIsInstance(resource.get_course_classes(ID)[0], ClassesModel)

    def test_demographics_methods(self):
        api = StubAPI(
            {
                "demographics": {"demographics": [demographic()]},
                f"demographics/{ID}": {"demographics": demographic()},
            }
        )
        resource = Demographics(api)

        self.assertIsInstance(resource.get_demographics()[0], DemographicsModel)
        self.assertIsInstance(resource.get_demographic(ID), DemographicsModel)

    def test_enrollments_methods(self):
        api = StubAPI(
            {
                "enrollments": {"enrollments": [enrollment()]},
                f"enrollments/{ID}": {"enrollment": enrollment()},
            }
        )
        resource = Enrollments(api)

        self.assertIsInstance(resource.get_enrollments()[0], EnrollmentsModel)
        self.assertIsInstance(resource.get_enrollment(ID), EnrollmentsModel)

    def test_orgs_methods(self):
        record = school() | {"dateLastModified": DATE}
        api = StubAPI({"orgs": {"orgs": [record]}, f"orgs/{ID}": {"org": record}})
        resource = Orgs(api)

        self.assertIsInstance(resource.get_orgs()[0], OrgsModel)
        self.assertIsInstance(resource.get_org(ID), OrgsModel)

    def test_terms_methods(self):
        api = StubAPI(
            {
                "terms": {"academicSessions": [academic_session()]},
                f"terms/{ID}": {"academicSession": academic_session()},
                f"terms/{ID}/classes": {"classes": [class_record()]},
                f"terms/{ID}/gradingPeriods": {
                    "academicSessions": [academic_session()]
                },
            }
        )
        resource = Terms(api)

        self.assertIsInstance(resource.get_terms()[0], AcademicSessionsModel)
        self.assertIsInstance(resource.get_term(ID), AcademicSessionsModel)
        self.assertIsInstance(resource.get_term_classes(ID)[0], ClassesModel)
        self.assertIsInstance(
            resource.get_term_grading_periods(ID)[0], AcademicSessionsModel
        )

    def test_grading_period_methods(self):
        api = StubAPI(
            {
                "gradingPeriods": {"academicSessions": [academic_session()]},
                f"gradingPeriods/{ID}": {"academicSession": academic_session()},
            }
        )
        resource = GradingPeriods(api)

        self.assertIsInstance(resource.get_grading_periods()[0], AcademicSessionsModel)
        self.assertIsInstance(resource.get_grading_period(ID), AcademicSessionsModel)

    def test_schools_methods(self):
        score_scale = {
            "sourcedId": ID,
            "status": "active",
            "dateLastModified": DATE,
            "metadata": {},
            "title": "Letter grade",
            "type": "letter",
            "class": ref(resource_type="class"),
            "course": ref(resource_type="course"),
            "scoreScaleValue": [],
        }
        class_group = {
            "sourcedId": ID,
            "status": "active",
            "dateLastModified": DATE,
            "metadata": {},
            "title": "Grade 9",
            "classes": [ref(resource_type="class")],
            "groupType": "grade",
        }
        responses = {
            f"schools/{ID}/scoreScales": {"scoreScales": [score_scale]},
            "schools": {"orgs": [school()]},
            f"schools/{ID}/classes": {"classes": [class_record()]},
            f"schools/{ID}/classes/{OTHER_ID}/enrollments": {
                "enrollments": [enrollment()]
            },
            f"schools/{ID}/classes/{OTHER_ID}/students": {"users": [student()]},
            f"schools/{ID}/classes/{OTHER_ID}/teachers": {"users": [teacher()]},
            f"schools/{ID}/classGroups": {"classGroups": [class_group]},
            f"schools/{ID}/courses": {"courses": [course()]},
            f"schools/{ID}/enrollments": {"enrollments": [enrollment()]},
            f"schools/{ID}": {"org": school()},
            f"schools/{ID}/students": {"users": [student()]},
            f"schools/{ID}/teachers": {"users": [teacher()]},
            f"schools/{ID}/terms": {"academicSessions": [academic_session()]},
        }
        resource = Schools(StubAPI(responses))

        checks = [
            (resource.get_school_score_scales(ID)[0], ScoreScales),
            (resource.get_schools()[0], SchoolModel),
            (resource.get_school_classes(ID)[0], ClassesModel),
            (resource.get_school_class_enrollments(ID, OTHER_ID)[0], EnrollmentsModel),
            (resource.get_school_class_students(ID, OTHER_ID)[0], StudentModel),
            (resource.get_school_class_teachers(ID, OTHER_ID)[0], TeacherModel),
            (resource.get_school_class_groups(ID)[0], ClassGroup),
            (resource.get_school_courses(ID)[0], CourseModel),
            (resource.get_school_enrollments(ID)[0], EnrollmentsModel),
            (resource.get_school(ID), SchoolModel),
            (resource.get_school_students(ID)[0], StudentModel),
            (resource.get_school_teachers(ID)[0], TeacherModel),
            (resource.get_school_terms(ID)[0], AcademicSessionsModel),
        ]
        for value, expected_type in checks:
            with self.subTest(expected_type=expected_type.__name__):
                self.assertIsInstance(value, expected_type)


if __name__ == "__main__":
    unittest.main()
