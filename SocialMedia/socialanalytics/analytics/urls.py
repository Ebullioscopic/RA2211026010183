from django.urls import path
from . import views

urlpatterns = [
    path('users', views.top_users, name='top_users'),
    path('posts', views.top_posts, name='top_posts'),
]
