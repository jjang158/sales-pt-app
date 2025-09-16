from django.urls import path
from . import views

urlpatterns = [
    # Consult
    path('/', views.save_consult, name='save_consult'),
    path('/analyze', views.analyze_consult, name='analyze_consult'),
    path('/list',views.consult_list, name='consult_list'),
    path('/cust',views.consult_cust, name='consult_cust'),
    #path('/todos/<int:id>', views.todo, name='todo')
    path('/detail', views.consult_detail, name='consult-detail'),
]