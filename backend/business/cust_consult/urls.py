from django.urls import path
from . import views

urlpatterns = [
    # Consult
    path('', views.save_consult, name='save_consult'),
    path('analyze', views.analyze_consult, name='analyze_consult'),
    #path('todos/<int:id>', views.todo, name='todo')
]