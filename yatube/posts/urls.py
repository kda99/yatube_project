from django.urls import path
from . import views

app_name = 'post_ns'

urlpatterns = [
    path('', views.index, name = 'index'),
    path('groups/<slug:slug>/', views.group_posts, name = 'post'),
]
