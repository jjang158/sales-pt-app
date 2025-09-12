from django.urls import path
from .views import ChatbotQueryView, DocumentVectorizing

urlpatterns = [
    path("chatbot/doc2Vec", DocumentVectorizing.as_view(), name="chatbot-query"),
    path("chatbot/query", ChatbotQueryView.as_view(), name="chatbot-query"),
]
