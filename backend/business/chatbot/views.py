from rest_framework.views import APIView
from ..common.doc_to_vector import process_pdfs
from ..common.response_format import response_suc, response_err

from .serializers import ChatbotRequestSerializer

class DocumentVectorizing(APIView):
    def post(self, request):
        try:
            total_count, suc_count = process_pdfs()
            print(f"total_count : {total_count}")
            print(f"suc_count : {suc_count}")
        except Exception as e:
            return response_err(500, str(e))
        
        return response_suc()

class ChatbotQueryView(APIView):
    def post(self, request):
        serializer = ChatbotRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return response_err(400, "잘못된 요청 형식")

        try:
            # 1. 질문 임베딩 생성
            embedding_response = openai.Embedding.create(
                input=question,
                model="text-embedding-ada-002"
            )
            query_embedding = embedding_response["data"][0]["embedding"]

            # 2. DB 유사도 검색 (consult + file detail)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, content, 'consult' as type,
                           1 - (embedding <=> cube(array[%s])) as similarity
                    FROM vector_consult_data
                    ORDER BY embedding <=> cube(array[%s])
                    LIMIT 3
                """, [query_embedding, query_embedding])
                consult_results = cursor.fetchall()

                cursor.execute("""
                    SELECT id, content, 'document' as type,
                           1 - (embedding <=> cube(array[%s])) as similarity
                    FROM vector_file_detail
                    ORDER BY embedding <=> cube(array[%s])
                    LIMIT 3
                """, [query_embedding, query_embedding])
                doc_results = cursor.fetchall()

            sources = []
            context_texts = []
            for row in consult_results + doc_results:
                sid, content, stype, sim = row
                sources.append({"type": stype, "id": sid, "excerpt": content[:200]})
                context_texts.append(content[:500])

            # 3. LLM 호출 (검색 결과 포함)
            messages = []
            for h in q_history:
                messages.append({"role": h["role"], "content": h["content"]})
            messages.append({
                "role": "system",
                "content": "너는 영업 지원 챗봇이야. 아래 자료를 참고해 사용자 질문에 답변해."
            })
            messages.append({
                "role": "user",
                "content": f"질문: {question}\n\n참고 자료:\n" + "\n---\n".join(context_texts)
            })

            chat_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages
            )
            llm_answer = chat_response["choices"][0]["message"]["content"]

            # 4. 최종 응답
            response_data = {
                "answer": llm_answer,
                "sources": sources,
            }
            return response_suc(response_data)

        except Exception as e:
            return response_err(500, f"서버 오류: {str(e)}")