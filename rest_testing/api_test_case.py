import json
from typing import Any, Callable, Dict, List, Optional, cast

from django.db import transaction
from django.http.response import HttpResponse
from django.test import TestCase
from django.utils.http import urlencode
from pydantic import TypeAdapter

from rest_testing.api_view_test_scenario import (
    APIViewTestScenario,
    ResponseBodyType,
)


class APITestCase(TestCase):
    """
    A subclass of Django's `TestCase` that provides methods for testing Django REST
    API views declaratively using test scenarios.

    Designed to be used with the `APIViewTestScenario` class, each scenario can
    include the request components (path/query parameters, request body/headers),
    the expected response components (status code, response body type/content), and
    extra assertions to be made on the response.

    This class provides methods for sending requests to the API view, asserting that
    a scenario succeed, and asserting that multiple scenarios succeed. It also includes
    methods for making assertions on the response, such as checking the status code,
    validating the response body type, and comparing the response body to the expected
    response body.

    Example:
    ```python
    from rest_testing import APITestCase, APIViewTestScenario

    class TestObjectAPI(APITestCase):
        def test_read_object(self):
            self.assertScenariosSucceed(
                method="GET",
                path="/api/objects/{id}",
                scenarios=[
                    APIViewTestScenario(
                        path_parameters={"id": 1},
                        request_headers={"HTTP_AUTHORIZATION": "Bearer 123"},
                        expected_response_status=200,
                        expected_response_body='{"id": 1, "name": "object-1"}',
                    ),
                    APIViewTestScenario(
                        path_parameters={"id": 2},
                        request_headers={"HTTP_AUTHORIZATION": "Bearer 123"},
                        expected_response_status=404,
                    ),
                    APIViewTestScenario(
                        path_parameters={"id": 2},
                        request_headers={"HTTP_AUTHORIZATION": "Bearer 456"},
                        expected_response_status=403,
                    ),
                    APIViewTestScenario(
                        path_parameters={"id": 2},
                        request_headers={},
                        expected_response_status=401,
                    ),
                ],
            )
    ```

    Note:
        When testing multiple scenarios, each scenario is run in a subtest and in a
        separate transaction savepoint to ensure that the scenarios are independent.
        The database changes are rolled back between each scenario to prevent side
        effects between scenarios.
    """

    def send_request(
        self,
        method: str,
        path: str,
        path_parameters: Optional[Dict[str, Any]] = None,
        query_parameters: Optional[Dict[str, Any]] = None,
        request_body: Optional[Dict[str, Any]] = None,
        request_headers: Optional[Dict[str, Any]] = None,
    ) -> HttpResponse:
        """
        Send a request to the API view with the given method, path, path parameters,
        query parameters, request body, and request headers.

        Args:
            method(str): The HTTP method of the request.
            path(str): The path of the request.
            path_parameters(dict, optional): The path parameters of the request.
            query_parameters(dict, optional): The query parameters of the request.
            request_body(dict, optional): The request body of the request.
            request_headers(dict, optional): The request headers of the request.

        Returns:
            HttpResponse: The response of the request.

        Example:
        ```python
        response = self.send_request(
            method="POST",
            path="/api/objects/{id}",
            path_parameters={"id": 1},
            query_parameters={},
            request_body={"name": "new name"},
            request_headers={"HTTP_AUTHORIZATION": "Bearer 123"},
        )
        ```
        """
        args: Dict[str, Any] = {
            "method": method,
            "path": path.format(**path_parameters or {}),
        }
        if query_parameters is not None:
            args["QUERY_STRING"] = urlencode(query_parameters, doseq=True)
        if request_body is not None:
            args["data"] = json.dumps(request_body)
        if request_headers is not None:
            args.update(request_headers)

        response = self.client.generic(**args)
        return cast(HttpResponse, response)

    def assertScenarioSucceed(
        self,
        method: str,
        path: str,
        scenario: APIViewTestScenario[ResponseBodyType],
        default_assertions: Optional[
            Callable[[HttpResponse, APIViewTestScenario[ResponseBodyType]], None]
        ] = None,
    ) -> None:
        """
        Assert that the given scenario succeeds when sent to the API view with the
        given method and path.

        Args:
            method(str): The HTTP method of the request.
            path(str): The path of the request.
            scenario(APIViewTestScenario): The scenario to test.
            default_assertions(callable, optional): The default assertions to make on
                the response if no assertions are provided in the scenario.

        Example:
        ```python
        self.assertScenarioSucceed(
            method="GET",
            path="/api/objects/{id}",
            scenario=APIViewTestScenario(
                path_parameters={"id": 1},
                request_headers={"HTTP_AUTHORIZATION": "Bearer 123"},
                expected_response_status=200,
                expected_response_body='{"id": 1, "name": "object-1"}',
            ),
        )
        ```
        """
        response = self.send_request(
            method=method,
            path=path,
            path_parameters=scenario.path_parameters,
            query_parameters=scenario.query_parameters,
            request_body=scenario.request_body,
            request_headers=scenario.request_headers,
        )

        if scenario.expected_response_status is not None:
            self.assertEqual(
                first=response.status_code, second=scenario.expected_response_status
            )

        if scenario.expected_response_body_type is not None:
            TypeAdapter(scenario.expected_response_body_type).validate_json(
                response.content
            )

        if isinstance(scenario.expected_response_body, bytes):
            self.assertEqual(
                first=response.content, second=scenario.expected_response_body
            )
        elif scenario.expected_response_body is not None:
            self.assertJSONEqual(
                raw=response.content.decode(),
                expected_data=scenario.expected_response_body,
            )

        assertions = scenario.assertions or default_assertions
        if assertions is not None:
            assertions(response, scenario)

    def assertScenariosSucceed(
        self,
        method: str,
        path: str,
        scenarios: List[APIViewTestScenario[ResponseBodyType]],
        default_assertions: Optional[
            Callable[[HttpResponse, APIViewTestScenario[ResponseBodyType]], None]
        ] = None,
    ) -> None:
        """
        Assert that the given scenarios succeed when sent to the API view with the
        given method and path.

        This method runs each scenario in a separate transaction savepoint to ensure
        that the scenarios are independent, and rolls back the database changes between
        each scenario.

        Args:
            method(str): The HTTP method of the request.
            path(str): The path of the request.
            scenarios(List[APIViewTestScenario]): The scenarios to test.
            default_assertions(callable, optional): The default assertions to make on
                the response if no assertions are provided in the scenarios.

        Example:
        ```python
        self.assertScenariosSucceed(
            method="DELETE",
            path="/api/objects/{id}",
            scenarios=[
                APIViewTestScenario(
                    path_parameters={"id": 1},
                    request_headers={"HTTP_AUTHORIZATION": "Bearer 123"},
                    expected_response_status=204,
                ),
                APIViewTestScenario(
                    path_parameters={"id": 1},
                    request_headers={"HTTP_AUTHORIZATION": "Bearer 456"},
                    expected_response_status=204,
                ),
                APIViewTestScenario(
                    path_parameters={"id": 1},
                    request_headers={"HTTP_AUTHORIZATION": "Bearer 789"},
                    expected_response_status=204,
                ),
            ],
        )
        ```
        """
        for scenario in scenarios:
            with self.subTest(scenario):
                sid = transaction.savepoint()
                try:
                    self.assertScenarioSucceed(
                        method=method,
                        path=path,
                        scenario=scenario,
                        default_assertions=default_assertions,
                    )
                finally:
                    transaction.savepoint_rollback(sid)
