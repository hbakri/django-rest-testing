from typing import Callable, Optional

import django.core.exceptions
import django.db
import pydantic
from django.http import HttpRequest, HttpResponse, JsonResponse


class ExceptionHandlingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    @staticmethod
    def process_exception(
        request: HttpRequest, exception: Exception
    ) -> Optional[HttpResponse]:
        if isinstance(exception, django.core.exceptions.ObjectDoesNotExist):
            return JsonResponse({"error": "Object does not exist"}, status=404)
        if isinstance(exception, django.core.exceptions.ValidationError):
            return JsonResponse({"error": exception.message_dict}, status=400)
        elif isinstance(exception, pydantic.ValidationError):
            return JsonResponse({"error": exception.errors()}, status=400)
