# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    template = 'posts/index.html'
    text = 'Это главная страница проекта Yatube'
    context = {
        'text': text
    }
    return render(request, template, context)


def group_posts(request, pk ):
    # return HttpResponse(f'Группа номер {pk}')
    template = 'posts/group_list.html'
    text = f'Здесь будет информация о группах проекта Yatube номер {pk}'
    context = {
        'text': text
    }
    return render(request, template, context)

