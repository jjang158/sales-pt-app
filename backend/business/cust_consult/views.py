from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
from .openaiservice import analyze_consult_text 
import json
from django.http import JsonResponse
from .models import Todo_list
from ..common.response_format import response_suc, response_err

#상담 정보 등록 API
@api_view(['POST'])
def save_consult(request):
    try:
        customer_id = request.data.get('customer_id')
        consult_text = request.data.get('consult_text')
        content_type = request.data.get('content_type')
        stages = request.data.get('stages', [])
        
        if not customer_id:
            return response_err(400,'customer_id는 필수입니다.')
            
        if not consult_text:
            return response_err(400,'consult_text는 필수입니다.')
        
        if not content_type:
            return response_err(400, 'content_type는 필수입니다.')
        
        if content_type not in ['voice','text']:
            return response_err(400, 'content_type는 voice또는 text여야 합니다.')
        
        if not stages:
            return response_err(400,'stages는 최소 1개 이상이어야 합니다.')
        
        cursor = connection.cursor()
        

        # stage 검증
        for stage in stages:
            stage_meta_id= stage.get('stage_meta_id')
            stage_name= stage.get('stage_name')
                
            if not stage_meta_id:
                return response_err(400,'stage_meta_id는 필수입니다.')
        
            if not stage_name:
                return response_err(400,'stage_name은 필수입니다.')
                
            if not isinstance(stage_meta_id, int) or stage_meta_id <= 0:
                return response_err(400, 'stage_meta_id는 양수여야 합니다.')

        cursor.execute(
            """INSERT INTO consult (customer_id, consult_text, content_type, consult_date)
            VALUES (%s, %s, %s, NOW()) RETURNING id""", [customer_id, consult_text, content_type])
        
        consult_id = cursor.fetchone()[0] # PostgreSQL 은 RETURNING id와 이 한줄이 필요하다고 하는데 이해가 잘 되지않음 나중에 재학습필요

        for stage in stages:
            stage_meta_id= stage.get('stage_meta_id')
            stage_name= stage.get('stage_name')
            if stage_meta_id and stage_name :
                cursor.execute("""INSERT INTO consult_stage (consult_id, stage_meta_id, stage_name, created_at)
                               VALUES (%s, %s, %s, NOW())""", [consult_id,stage_meta_id,stage_name])
        cursor.close()
        
        return response_suc()
        
    except Exception as e:
        return response_err(500,f'저장 중 오류가 발생했습니다: {str(e)}')
    
# 상담 LLM 요청 API
@api_view(['POST'])
def analyze_consult(request):
    try:
        text_to_summarize = request.data.get('text_to_summarize')
        
        if not text_to_summarize:
            return response_err(400,'text_to_summarize는 필수입니다')
        
        # OpenAI 분석 호출
        result = analyze_consult_text(text_to_summarize)
        
        return response_suc(result)
        
    except json.JSONDecodeError:
        return response_err(500,'AI 응답을 JSON으로 파싱할 수 없습니다.')
    
    except Exception as e:
        return response_err(500,f'분석 중 오류가 발생했습니다: {str(e)}')

# Todo List 조회 API
@api_view(['GET'])
def todo(request):
    cursor = connection.cursor()
    try:
        sql = "SELECT id, customer_id, due_date, title, description, is_completed, created_at FROM todo_list WHERE 1=1"
        
        # customer_id 필터
        customer_id = request.GET.get('customer_id')
        if customer_id:
            try:
                customer_id = int(customer_id)
                sql += f" AND customer_id = {customer_id}"
            except ValueError:
                return response_err(400,'customer_id는 정수여야 합니다.')
        
        # 완료 여부 필터
        is_completed = request.GET.get('is_completed')
        if is_completed == 'true':
            sql += " AND is_completed = true"
        elif is_completed == 'false':
            sql += " AND is_completed = false"
            
        cursor.execute(sql)
        results = cursor.fetchall()
        
        todos = []
        for row in results:
            todos.append({
                'id': row[0],
                'customer_id': row[1], 
                'due_date': row[2].isoformat() if row[2] else None,
                'title': row[3],
                'description': row[4],
                'is_completed': row[5],
                'created_at': row[6].isoformat() if row[6] else None
            })
            
        return response_suc(todos)
        
    except Exception as e:
        return response_err(500,f'오류: {str(e)}')
    finally:
        cursor.close()