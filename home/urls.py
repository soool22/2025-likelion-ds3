from django.urls import path
from .views import *

app_name="home"

urlpatterns = [
    path('main/', main, name='main'), # main 연결  
]
