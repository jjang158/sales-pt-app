from django.urls import path
from . import views

urlpatterns = [
    path('/', views.todo, name='todo'),
    path('/<int:id>', views.todo, name='todo'),
    path('/complete', views.todo_complete, name="todo_complete")
]