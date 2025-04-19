from django.urls import path
from . import views

app_name = "Interview"

urlpatterns = [
    path("", views.index, name="index"),
    path("add", views.add, name="add"),
    path("<int:id>", views.show, name="show")
]
