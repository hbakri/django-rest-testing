# Django REST Testing
[![Tests](https://github.com/hbakri/django-rest-testing/actions/workflows/tests.yml/badge.svg)](https://github.com/hbakri/django-rest-testing/actions)
[![Coverage](https://img.shields.io/codecov/c/github/hbakri/django-rest-testing/main.svg?label=coverage&logo=codecov&logoColor=white)](https://codecov.io/gh/hbakri/django-rest-testing)
[![PyPI version](https://img.shields.io/pypi/v/django-rest-testing?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/django-rest-testing/)
[![Downloads](https://static.pepy.tech/badge/django-rest-testing/month)](https://pepy.tech/project/django-rest-testing)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![MyPy](https://img.shields.io/badge/mypy-checked-blue.svg)](https://github.com/python/mypy)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

![Django REST Testing](https://raw.githubusercontent.com/hbakri/django-rest-testing/main/docs/assets/images/django-rest-testing-logo.png)

**Django REST Testing** is a small, [declarative](https://en.wikipedia.org/wiki/Declarative_programming), opinionated, and yet powerful tool designed to streamline the development of tests for **RESTful** endpoints within [Django](https://github.com/django/django). This package embraces best practices to ensure efficient and robust endpoint testing, allowing developers to focus on what truly matters when testing their applications: ensuring they work as expected.

Originally integrated within [Django Ninja CRUD](https://github.com/hbakri/django-ninja-crud), it has evolved into a standalone package. This evolution enables developers to test their RESTful endpoints with ease and precision, regardless of the framework in use.

By using a **scenario-based** test case approach, this package empowers developers to
rigorously test RESTful endpoints under varied conditions and inputs. Each scenario
specifically targets distinct endpoint behaviors—ranging from handling valid and
invalid inputs to managing nonexistent resources and enforcing business rules.

This modular approach breaks tests into distinct, manageable units, streamlining the testing
process, enhancing clarity and maintainability, and ensuring comprehensive
coverage — making it an indispensable tool for modern web development.

## 📝 Requirements

[![Python versions](https://img.shields.io/pypi/pyversions/django-rest-testing.svg?color=306998&label=python&logo=python&logoColor=white)](https://github.com/python/cpython)
[![Django versions](https://img.shields.io/badge/3.2_|_4.1_|_4.2_|_5.0-blue?color=0C4B33&label=django&logo=django&logoColor=white)](https://github.com/django/django)
[![Pydantic versions](https://img.shields.io/badge/>=2.0-blue?color=black&label=pydantic&logo=pydantic&logoColor=white)](https://github.com/vitalik/django-ninja)

## ⚒️ Installation
```bash
pip install django-rest-testing
```
For more information, see the [installation guide](https://django-rest-testing.readme.io/docs/02-installation).

## 👨‍🎨 Example
Let's imagine you're building a system for a university and you have a model called `Department`. Each department in your university has a unique title.

```python
# examples/models.py
import uuid
from django.db import models

class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True)
```

To interact with this data, we need a way to convert it between Python objects and a
format that's easy to read and write (like JSON). We can use [Pydantic](
https://github.com/pydantic/pydantic) to define schemas for our data:

```python
# examples/schemas.py
import uuid
from pydantic import BaseModel

class DepartmentIn(BaseModel):
    title: str

class DepartmentOut(BaseModel):
    id: uuid.UUID
    title: str
```

The `DepartmentIn` schema defines what data we need when creating or updating a department.
The `DepartmentOut` schema defines what data we'll provide when retrieving a department.

Now, we take pride in the simplicity and directness of using vanilla Django to
handle our endpoints. It’s like cooking a gourmet meal with just a few basic
ingredients — surprisingly satisfying and impressively functional.

```python
# examples/views.py
import uuid

from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods

from examples.models import Department
from examples.schemas import DepartmentIn, DepartmentOut


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
```

There you have it—a minimalistic yet powerful approach to handling RESTful operations
in Django. Up next, let’s dive into how declarative testing makes validating these
endpoints both efficient and straightforward.

```python
# examples/tests.py
import uuid

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
```

As you can see, the `APITestCase` class provides a simple and intuitive way to
define test scenarios. Each scenario specifies the expected request and response,
making it easy to understand what's being tested. This approach not only simplifies
the testing process but also enhances the **clarity** and **maintainability** of
test suites.

## 📚 Documentation
For more information, see the [documentation](https://django-rest-testing.readme.io/).

## 🫶 Support
First and foremost, a heartfelt thank you for taking an interest in this project. If it has been helpful to you or you believe in its potential, kindly consider giving it a star on GitHub. Such recognition not only fuels my drive to maintain and improve this work but also makes it more visible to new potential users and contributors.

![GitHub Repo stars](https://img.shields.io/github/stars/hbakri/django-rest-testing?style=social)

If you've benefited from this project or appreciate the dedication behind it, consider showing further support. Whether it's the price of a coffee, a word of encouragement, or a sponsorship, every gesture adds fuel to the open-source fire, making it shine even brighter. ✨

[![Sponsor](https://img.shields.io/badge/sponsor-donate-pink?logo=github-sponsors&logoColor=white)](https://github.com/sponsors/hbakri)
[![Buy me a coffee](https://img.shields.io/badge/buy_me_a_coffee-donate-pink?logo=buy-me-a-coffee&logoColor=white)](https://www.buymeacoffee.com/hbakri)

Your kindness and support make a world of difference. Thank you! 🙏
