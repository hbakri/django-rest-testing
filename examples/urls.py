from django.urls import path

from examples import views

urlpatterns = [
    path("departments/", views.list_create_departments),
    path("departments/<uuid:id>", views.read_update_delete_department),
]
