from rest_framework import serializers

class ChatbotRequestSerializer(serializers.Serializer):
    # 필수 질문
    question = serializers.CharField(
        required=True,
        help_text="사용자 질문"
    )

    # 대화 히스토리
    q_history = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        help_text="이전 대화 기록"
    )
