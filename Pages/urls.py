from django.urls import path
from . import views

app_name = "Page"

urlpatterns = [
    path('', views.index, name = "index")
]
