import uuid
from typing import List

from examples.models import Department
from examples.schemas import DepartmentOut
from rest_testing import APITestCase, APIViewTestScenario


class TestDepartmentViewSet(APITestCase):
    department_1: Department
    department_2: Department

    @classmethod
    def setUpTestData(cls):
        cls.department_1 = Department.objects.create(title="department-1")
        cls.department_2 = Department.objects.create(title="department-2")

    def test_list_departments(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/departments/",
            scenarios=[
                APIViewTestScenario(
                    query_parameters={"order_by": ["title"]},
                    expected_response_status=200,
                    expected_response_body_type=List[DepartmentOut],
                    expected_response_body=[
                        {
                            "id": str(self.department_1.id),
                            "title": self.department_1.title,
                        },
                        {
                            "id": str(self.department_2.id),
                            "title": self.department_2.title,
                        },
                    ],
                ),
            ],
        )

    def test_create_department(self):
        self.assertScenariosSucceed(
            method="POST",
            path="/api/departments/",
            scenarios=[
                APIViewTestScenario(
                    request_body={"title": "new_title"},
                    expected_response_status=201,
                    expected_response_body_type=DepartmentOut,
                ),
                APIViewTestScenario(
                    request_body={"title": "department-1"},
                    expected_response_status=400,
                ),
                APIViewTestScenario(
                    request_body={"title": [1]},
                    expected_response_status=400,
                ),
            ],
        )

    def test_read_department(self):
        self.assertScenariosSucceed(
            method="GET",
            path="/api/departments/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    expected_response_status=200,
                    expected_response_body_type=DepartmentOut,
                    expected_response_body={
                        "id": str(self.department_1.id),
                        "title": self.department_1.title,
                    },
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    expected_response_status=404,
                ),
            ],
        )

    def test_update_department(self):
        self.assertScenariosSucceed(
            method="PUT",
            path="/api/departments/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    request_body={"title": "new_title"},
                    expected_response_status=200,
                    expected_response_body_type=DepartmentOut,
                    expected_response_body={
                        "id": str(self.department_1.id),
                        "title": "new_title",
                    },
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    request_body={"title": "new_title"},
                    expected_response_status=404,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    request_body={"title": [1]},
                    expected_response_status=400,
                ),
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    request_body={"title": self.department_2.title},
                    expected_response_status=400,
                ),
            ],
        )

    def test_delete_department(self):
        self.assertScenariosSucceed(
            method="DELETE",
            path="/api/departments/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": self.department_1.id},
                    expected_response_status=204,
                    expected_response_body=b"",
                ),
                APIViewTestScenario(
                    path_parameters={"id": uuid.uuid4()},
                    expected_response_status=404,
                ),
            ],
        )
