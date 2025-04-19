from django.urls import path
from . import views

app_name = "Interview"

urlpatterns = [
    path("", views.index, name="index")
]
