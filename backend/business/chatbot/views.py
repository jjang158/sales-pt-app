from rest_framework.views import APIView
from openai import OpenAI
import os

from .serializers import ChatbotRequestSerializer
from ..common.doc_to_vector import process_pdfs
from ..common.response_format import response_suc, response_err
from .vec_search_service import consult_search, document_search

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        print('챗봇 시작')
        serializer = ChatbotRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return response_err(400, "잘못된 요청 형식")

        try:
            v = serializer.validated_data
            question = v.get("question")
            q_history = v.get("q_history", [])

            # 1. 질문 임베딩
            emb = client.embeddings.create(
                input=question,
                model="text-embedding-ada-002"
            )
            query_embedding = emb.data[0].embedding
            
            # 2. 히스토리 임베딩
            recent_history = " ".join([h["content"] for h in q_history[-4:]])
            context_query = f"{recent_history}\n사용자 질문: {question}"

            emb_ctx = client.embeddings.create(
                input=context_query,
                model="text-embedding-ada-002"
            )
            context_embedding = emb_ctx.data[0].embedding

            # 2. 백터 DB 조회
            print('query_embedding 조회')
            consult_results_q = consult_search(query_embedding)
            doc_results_q = document_search(query_embedding)

            print('context_embedding 조회')
            consult_results_ctx = consult_search(context_embedding)
            doc_results_ctx = document_search(context_embedding)

            # 결과 합치기 (중복 제거)
            all_results = consult_results_q + doc_results_q + consult_results_ctx + doc_results_ctx

            sources = []
            context_texts = []
            seen = set()
            for row in all_results:
                file_info, content, stype, sim = row
                
                # 중복 제거 (파일+내용 일부 기준)
                key = (file_info, content[:200])
                if key in seen:
                    continue
                seen.add(key)
                
                sources.append({"type": stype, "file_info": file_info, "excerpt": content[:200]})
                context_texts.append(content[:500])

            # 3. LLM 호출 (검색 결과 포함)
            messages = []
            for h in q_history:
                messages.append({"role": h["role"], "content": h["content"]})
            # system prompt
            messages.append({
                "role": "system",
                "content": """당신은 회사의 영업 지원 챗봇입니다. 주요 역할은 두 가지 자료를 기반으로 고객 질문에 답변해주세요:
                            1. 고객 상담 기록 (consult) : 실제 고객과의 대화, 요구사항, 이슈 내용이 담김
                            2. 회사 내부 영업 가이드 (document) : 제품, 서비스, 정책, 매뉴얼 등 공식 지침
                            응답 시 반드시 아래 원칙을 따라 작성한다:
                            - 제공된 "참고 자료"를 최우선으로 활용
                            - 참고 자료에 없는 내용은 "자료에 해당 내용이 없습니다"라고 답한다
                            - 필요하면 consult(상담)과 document(가이드)를 구분해서 인용한다
                            - 응답은 대화하는 느낌으로 친절하고 신뢰감을 주는 톤으로 작성한다"""
            })
            # user prompt
            messages.append({
                "role": "user",
                "content": f"사용자 질문: {question}\n\n참고 자료:\n" + "\n---\n".join(context_texts)
            })

            print('LLM 호출')
            chat_response = client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=300,
                temperature = 0.2
            )
            llm_answer = chat_response.choices[0].message.content

            # 4. 최종 응답
            response_data = {
                "answer": llm_answer,
                "sources": sources,
            }
            print('챗봇 종료')
            return response_suc(response_data)

        except Exception as e:
            return response_err(500, f"서버 오류: {str(e)}")