import unittest

from pydantic import ValidationError

from infinitecampusapi.classes.Classes import (
    CategoriesModel,
    LineItemsModel,
    ResultsModel,
)
from infinitecampusapi.classes.extras import UserId, V1P2UserRoleBase, guidRef

from test_resources import DATE, ID, ref


class ModelTests(unittest.TestCase):
    def test_reference_and_user_id_models(self):
        reference = guidRef(**ref())
        user_id = UserId(identifier="42", type="studentNumber")

        self.assertEqual(str(reference.sourcedId), ID)
        self.assertEqual(user_id.identifier, "42")

    def test_user_role_model(self):
        role = V1P2UserRoleBase(
            beginDate=DATE,
            endDate=DATE,
            roleType="primary",
            role="student",
            org=ref(),
        )

        self.assertEqual(role.role, "student")
        self.assertEqual(str(role.org.sourcedId), ID)

    def test_category_model(self):
        category = CategoriesModel(
            sourcedId=ID,
            status="active",
            dateLastModified=DATE,
            title="Homework",
            weight=0.25,
        )

        self.assertEqual(category.weight, 0.25)

    def test_line_item_model(self):
        line_item = LineItemsModel(
            sourcedId=ID,
            status="active",
            dateLastModified=DATE,
            title="Assignment 1",
            description="Practice",
            assignDate=DATE,
            dueDate=DATE,
            resultValueMin=0,
            resultValueMax=100,
            s_class=ref(resource_type="class"),
            category=ref(resource_type="category"),
            gradingPeriod=ref(resource_type="academicSession"),
            school=ref(resource_type="org"),
            academicSession=ref(resource_type="academicSession"),
            scoreScale=ref(resource_type="scoreScale"),
        )

        self.assertEqual(line_item.resultValueMax, 100)

    def test_result_model(self):
        result = ResultsModel(
            sourcedId=ID,
            status="active",
            dateLastModified=DATE,
            score=95,
            textScore="A",
            scoreDate=DATE,
            comment="Great work",
            scoreStatus="fully graded",
            missing="false",
            incomplete="false",
            late="false",
            inProgress="false",
            s_class=ref(resource_type="class"),
            student=ref(resource_type="student"),
            lineItem=ref(resource_type="lineItem"),
        )

        self.assertEqual(result.score, 95)

    def test_invalid_uuid_is_rejected(self):
        with self.assertRaises(ValidationError):
            CategoriesModel(
                sourcedId="not-a-uuid",
                status="active",
                dateLastModified=DATE,
                title="Homework",
                weight=1,
            )


if __name__ == "__main__":
    unittest.main()
