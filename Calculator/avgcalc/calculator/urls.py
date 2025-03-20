# calculator/urls.py
from django.urls import path
from .views import average_calculator

urlpatterns = [
    path('numbers/<str:numberid>/', average_calculator, name='average_calculator'),
]
