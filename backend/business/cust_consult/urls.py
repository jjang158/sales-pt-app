from django.urls import path
from . import views

urlpatterns = [
    # Consult
    path('save/', views.save_consult, name='save_consult'),
]