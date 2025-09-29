from django.urls import path
from .views import ChatbotQueryView, ChatbotQueryView2, DocumentVectorizing, InsuranceTermsVectorizer

urlpatterns = [
    path("doc2Vec", DocumentVectorizing.as_view(), name="chatbot-query"),
    path("query", ChatbotQueryView.as_view(), name="chatbot-query"),
    path("query2", ChatbotQueryView2.as_view(), name="chatbot-query"),
    path('upload',InsuranceTermsVectorizer.as_view(), name='insurance_upload')
]
