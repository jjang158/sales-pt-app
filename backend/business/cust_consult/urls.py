from django.urls import path
from . import views

urlpatterns = [
    # Consult
    path('consult/save/', views.save_consult, name='save_consult'),

    # Consult_stage
    path('consult_stage/save/', views.save_consult_stage, name='save_consult_stage')
]