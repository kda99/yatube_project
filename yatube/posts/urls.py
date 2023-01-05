from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('groups/<slug:pk>/', views.group_posts),
]
