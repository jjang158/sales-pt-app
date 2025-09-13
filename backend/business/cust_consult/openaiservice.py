import json
import os
from openai import OpenAI
from django.db import connection

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_sales_stages():
    """DB에서 영업단계 정보 조회"""
    cursor = connection.cursor()
    cursor.execute("select id, concat(name,description) from sales_stage_meta")
    stages = cursor.fetchall()
    cursor.close()
    
    stage_list = []
    for stage in stages:
        stage_list.append(f"- {stage[1]}: ID {stage[0]}")
    
    return "\n".join(stage_list)

def analyze_consult_text(text_to_summarize):
    # DB에서 영업단계 정보 조회
    sales_stages = get_sales_stages()
    
    SYSTEM_PROMPT = f"""당신은 보험 상담 내용을 분석하여 요약과 영업 단계를 분류하는 전문가입니다.

**영업 단계 정의:**
{sales_stages}

**분석 지침:**
1. 상담 내용을 면밀히 분석하여 해당하는 모든 영업 단계를 찾으세요
2. 하나의 상담에는 보통 2-3개의 단계가 포함됩니다
3. 각 단계별로 신뢰도를 0.1~1.0 사이로 정확히 평가하세요
4. 신뢰도가 0.6 이상인 단계들을 모두 포함하세요

**요약 규칙 (매우 중요):**
- 고객 이름이 있으면 반드시 포함
- 전화번호가 있으면 반드시 포함 (010-1234-5678 형태 그대로)
- 시간, 장소 정보가 있으면 반드시 포함
- 핵심 내용만 간결하게
- 불필요한 수사나 연결어 제거

**중요:** name은 위에서 제공된 정확한 단계명을 사용하세요.

반드시 아래 JSON 구조로만 응답하세요:

{{
    "summary": "상담 내용을 육하원칙을 살려서 핵심요약",
    "stages": [
        {{
            "id": 영업단계ID(숫자),
            "name": "위에서 제공된 정확한 단계명",
            "confidence": 신뢰도(0~1 소수점)
        }},
        {{
            "id": 영업단계ID(숫자),
            "name": "위에서 제공된 정확한 단계명", 
            "confidence": 신뢰도(0~1 소수점)
        }}
    ]
}}"""

    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {
                    'role': 'system',
                    'content': SYSTEM_PROMPT
                },
                {
                    'role': 'user',
                    'content': f"""다음 상담 내용을 분석하여 해당하는 모든 영업 단계를 찾아 분류해주세요:

                    {text_to_summarize}

                    상담 과정에서 일어난 모든 영업 활동을 고려하여 응답해주세요."""
                }
            ],
            temperature=0.1  # 더 일관된 결과를 위해 낮춤
        )
        
        result_text = response.choices[0].message.content
        print(f"OpenAI 응답: {result_text}")  # 디버깅용
        
        return json.loads(result_text)
        
    except Exception as e:
        print(f"OpenAI API 오류: {str(e)}")
        raise e