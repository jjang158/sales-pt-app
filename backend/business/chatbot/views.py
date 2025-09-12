from rest_framework.views import APIView
from common.doc_to_vector import process_pdfs
from common.response_format import response_suc, response_err

from .serializers import ChatbotRequestSerializer

class DocumentVectorizing(APIView):
    def post(self, request):
        try:
            process_pdfs()
            return response_suc()
        except Exception as e:
            return response_err(500, str(e))


class ChatbotQueryView(APIView):
    def post(self, request):
        serializer = ChatbotRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return response_err(400, "잘못된 요청 형식")

        validated = serializer.validated_data
        question = validated.get("question")
        q_history = validated.get("q_history", [])

        # 여기서 DB 상담 내역 & 문서 검색 + LLM 호출 로직 수행
        # 예: answer, sources = generate_chatbot_answer(question, q_history)

        answer = f"질문 '{question}' 에 대한 모의 응답입니다."
        sources = [
            {"type": "consult", "id": "201", "excerpt": "고객이 보험 상품 A에 대해 문의"},
            {"type": "document", "id": "product_manual_v3", "excerpt": "보험 상품 A 설명"}
        ]

        response_data = {"answer": answer,
                        "sources": sources}
        return response_suc(response_data)
