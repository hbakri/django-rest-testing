import uuid
from unittest.mock import Mock

from django.http import HttpResponse

from examples.schemas import DepartmentOut
from rest_testing.api_test_case import APITestCase, APIViewTestScenario


class TestAPITestCase(APITestCase):
    def setUp(self):
        self.client = Mock()

    def test_send_request(self):
        self.send_request(
            method="POST",
            path="/api/departments/{id}",
            path_parameters={"id": 1},
            query_parameters={},
            request_body={"title": "new title"},
            request_headers={"HTTP_AUTHORIZATION": "Bearer 123"},
        )
        self.client.generic.assert_called_with(
            method="POST",
            path="/api/departments/1",
            QUERY_STRING="",
            data='{"title": "new title"}',
            HTTP_AUTHORIZATION="Bearer 123",
        )

    def test_assert_scenario_succeed(self):
        self.client.generic.return_value = Mock(
            spec=HttpResponse,
            status_code=200,
            content=b'{"id": "3b13b5f4-150d-494e-8649-ed6e3f58c003", "title": "department-1"}',
        )

        self.assertScenarioSucceed(
            method="GET",
            path="/api/departments/{id}",
            scenario=APIViewTestScenario(
                path_parameters={
                    "id": uuid.UUID("3b13b5f4-150d-494e-8649-ed6e3f58c003")
                },
                expected_response_status=200,
                expected_response_body_type=DepartmentOut,
                assertions=lambda response, scenario: None,
            ),
        )

        with self.assertRaises(AssertionError):
            self.client.generic.return_value = Mock(spec=HttpResponse, status_code=404)
            self.assertScenarioSucceed(
                method="POST",
                path="/api/departments/",
                scenario=APIViewTestScenario(
                    expected_response_status=201,
                    expected_response_body_type=DepartmentOut,
                    assertions=lambda response, scenario: None,
                ),
            )
