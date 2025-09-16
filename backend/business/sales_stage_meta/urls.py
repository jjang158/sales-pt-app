from django.urls import path
from .views import SalesStageMetaView

urlpatterns = [
    path("", SalesStageMetaView.as_view(), name="sales stage meta"),
]
