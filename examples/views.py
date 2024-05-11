import uuid
from typing import List

from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from pydantic import TypeAdapter

from examples.models import Department
from examples.schemas import DepartmentIn, DepartmentOut, DepartmentQuery


@require_http_methods(["GET", "POST"])
def list_create_departments(request: HttpRequest):
    if request.method == "GET":
        query_parameters = DepartmentQuery.model_validate(request.GET)
        departments = Department.objects.order_by(*query_parameters.order_by).all()
        response_body = TypeAdapter(List[DepartmentOut]).dump_json(list(departments))
        return HttpResponse(content=response_body, status=200)

    elif request.method == "POST":
        request_body = DepartmentIn.model_validate_json(request.body)
        department = Department(**request_body.dict())
        department.full_clean()
        department.save()
        response_body = DepartmentOut.model_validate(department, from_attributes=True)
        return HttpResponse(content=response_body.model_dump_json(), status=201)


@require_http_methods(["GET", "PUT", "DELETE"])
def read_update_delete_department(request: HttpRequest, id: uuid.UUID):
    department = Department.objects.get(id=id)

    if request.method == "GET":
        response_body = DepartmentOut.model_validate(department, from_attributes=True)
        return HttpResponse(content=response_body.model_dump_json(), status=200)

    elif request.method == "PUT":
        request_body = DepartmentIn.model_validate_json(request.body)
        for key, value in request_body.dict().items():
            setattr(department, key, value)

        department.full_clean()
        department.save()
        response_body = DepartmentOut.model_validate(department, from_attributes=True)
        return HttpResponse(content=response_body.model_dump_json(), status=200)

    elif request.method == "DELETE":
        department.delete()
        return HttpResponse(content=b"", status=204)
