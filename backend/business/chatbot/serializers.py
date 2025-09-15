from rest_framework import serializers

class ChatHistorySerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "assistant"])
    content = serializers.CharField(help_text="이전 대화 기록")


class ChatbotRequestSerializer(serializers.Serializer):
    question = serializers.CharField(required=True, help_text="사용자 질문")
    q_history = ChatHistorySerializer(many=True, required=False)
