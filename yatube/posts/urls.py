from django.urls import path
from . import views

app_name = 'post_ns'

urlpatterns = [
    path('', views.index, name = 'index'),
    path('groups/<slug:pk>/', views.group_posts, name = 'post'),
]
