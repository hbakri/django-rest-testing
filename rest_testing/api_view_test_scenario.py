from typing import Any, Callable, Dict, Generic, Optional, Type, TypeVar

from django.http import HttpResponse

ResponseBodyType = TypeVar("ResponseBodyType")


class APIViewTestScenario(Generic[ResponseBodyType]):
    """
    A class that represents a single test scenario for a Django REST API view.
    This includes the request components (path, query parameters, request body,
    request headers), the expected response components (status code, body type,
    body), and assertions to be made on the response.

    Args:
        description (str, optional): A description of the test scenario.
        path_parameters (dict, optional): The path parameters for the request.
        query_parameters (dict, optional): The query parameters for the request.
        request_body (dict, optional): The request body for the request.
        request_headers (dict, optional): The request headers for the request.
        expected_response_status (int, optional): The expected status code of the response.
        expected_response_body_type (type, optional): The expected type of the response body.
        expected_response_body (Any, optional): The expected response body.
        assertions (callable, optional): A function that takes the response and the
            scenario as arguments and makes additional assertions on the response.

    Example:
    ```python
    scenario = APIViewTestScenario(
        path_parameters={"id": 1},
        query_parameters={},
        request_body={"title": "new title"},
        request_headers={"HTTP_AUTHORIZATION": "Bearer 123"},
        expected_response_status=200,
        expected_response_body_type=DepartmentOut,
        expected_response_body={"id": 1, "title": "new title"},
        assertions=lambda response, scenario: None,
    )
    ```

    Note:
        This class is generic over the type of the response body, which allows for
        type-checking of the expected response body type. Indeed, the
        `expected_response_body_type` attribute is used to validate the response body
        type using Pydantic's [TypeAdapter](https://docs.pydantic.dev/latest/api/type_adapter/#pydantic.type_adapter.TypeAdapter).
    """

    def __init__(
        self,
        description: Optional[str] = None,
        path_parameters: Optional[Dict[str, Any]] = None,
        query_parameters: Optional[Dict[str, Any]] = None,
        request_body: Optional[Dict[str, Any]] = None,
        request_headers: Optional[Dict[str, Any]] = None,
        expected_response_status: Optional[int] = None,
        expected_response_body_type: Optional[Type[ResponseBodyType]] = None,
        expected_response_body: Optional[Any] = None,
        assertions: Optional[
            Callable[[HttpResponse, "APIViewTestScenario[ResponseBodyType]"], None]
        ] = None,
    ) -> None:
        self.description = description
        self.path_parameters = path_parameters
        self.query_parameters = query_parameters
        self.request_body = request_body
        self.request_headers = request_headers
        self.expected_response_status = expected_response_status
        self.expected_response_body_type = expected_response_body_type
        self.expected_response_body = expected_response_body
        self.assertions = assertions

    def __str__(self) -> str:
        lines = ["APIViewTestScenario:"]
        for key, value in self.__dict__.items():
            if value is not None:
                lines.append(f"\t{key}={value}")
        return "\n".join(lines)
