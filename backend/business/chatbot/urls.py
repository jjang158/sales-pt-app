from django.urls import path
from .views import ChatbotQueryView, DocumentVectorizing, InsuranceTermsVectorizer

urlpatterns = [
    path("doc2Vec", DocumentVectorizing.as_view(), name="chatbot-query"),
    path("query", ChatbotQueryView.as_view(), name="chatbot-query"),
    path('upload',InsuranceTermsVectorizer.as_view(), name='insurance_upload')
]
