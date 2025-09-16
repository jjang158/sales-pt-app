from rest_framework.decorators import api_view
from django.db import connection
from .openaiservice import analyze_consult_text 
from .models import Consult, TodoList
from .serializers import ConsultSerializer, TodoSerializer
import json
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
        consult_text = request.data.get('consult_text')
        
        if not consult_text:
            return response_err(400,'consult_text는 필수입니다')
        
        # OpenAI 분석 호출
        result = analyze_consult_text(consult_text)
        
        return response_suc(result)
        
    except json.JSONDecodeError:
        return response_err(500,'AI 응답을 JSON으로 파싱할 수 없습니다.')
    
    except Exception as e:
        return response_err(500,f'분석 중 오류가 발생했습니다: {str(e)}')

# 상담내역 리스트 조회
@api_view(['GET'])
def consult_list(request):
    cursor = connection.cursor()
    try:
        customer_name = request.GET.get('customer_name')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        sql = """
        SELECT 
            c.name,
            (SELECT COUNT(*) FROM consult con 
             WHERE con.customer_id = c.id AND con.content_type = 'voice') as consult_count,
            (SELECT COUNT(*) FROM consult con 
             WHERE con.customer_id = c.id) as action_count,
            (SELECT COUNT(*) FROM todo_list t 
             WHERE t.customer_id = c.id AND t.is_completed = false) as pending_count,
            (SELECT con.consult_text FROM consult con 
             WHERE con.customer_id = c.id AND con.content_type = 'voice'
             ORDER BY con.consult_date DESC LIMIT 1) as latest_voice
        FROM customer c
        WHERE 1=1
        """
        
        if customer_name:
            sql += f" AND c.name LIKE '%{customer_name}%'"
        
        # 날짜 필터
        if start_date or end_date:
            sql += " AND EXISTS (SELECT 1 FROM consult con WHERE con.customer_id = c.id"
            
            if start_date:
                sql += f" AND con.consult_date >= '{start_date}'"
                
            if end_date:
                sql += f" AND con.consult_date <= '{end_date}'"
            
            sql += ")"
        
        sql += " ORDER BY c.name"
        
        cursor.execute(sql)
        results = cursor.fetchall()
        
        customers = []
        for row in results:
            customers.append({
                'customer_name': row[0],
                'consult_count': row[1] or 0,
                'action_count': row[2] or 0,
                'pending_count': row[3] or 0,
                'latest_voice': row[4]
            })
        
        return response_suc({'list': customers})
        
    except Exception as e:
        return response_err(500, f'조회 중 오류가 발생했습니다: {str(e)}')
    finally:
        cursor.close()

# 상담내역 상세조회1 - 고객정보
@api_view(['GET'])
def consult_cust(request):
    cursor = connection.cursor()
    try:
        customer_id = request.GET.get('customer_id')
        
        if not customer_id:
            return response_err(400, 'customer_id는 필수입니다.')
        
        try:
            customer_id = int(customer_id)
        except ValueError:
            return response_err(400, 'customer_id는 정수여야 합니다.')
        
        sql = """
        SELECT 
            c.name,
            c.email,
            c.phone_number,
            (SELECT COUNT(*) FROM consult con 
             WHERE con.customer_id = c.id AND con.content_type = 'voice') as consult_count,
            (SELECT COUNT(*) FROM consult con 
             WHERE con.customer_id = c.id) as action_count,
            (SELECT COUNT(*) FROM todo_list t 
             WHERE t.customer_id = c.id AND t.is_completed = false) as pending_count
        FROM customer c
        WHERE c.id = %s
        """
        
        cursor.execute(sql, [customer_id])
        result = cursor.fetchone()
        
        if not result:
            return response_err(400, '해당 고객을 찾을 수 없습니다.')
        
        customer_info = {
            'cust_name': result[0],
            'email': result[1],
            'phone_number': result[2],
            'consult_count': result[3] or 0,
            'action_count': result[4] or 0,
            'pending_count': result[5] or 0
        }
        
        return response_suc({
            'cust_info': customer_info
        })
        
    except Exception as e:
        return response_err(500, f'조회 중 오류가 발생했습니다: {str(e)}')
    finally:
        cursor.close()

#상담내역 상세조회 API
@api_view(['GET'])
def consult_detail(request):
    customer_id = request.query_params.get("customer_id")
    tab_type = request.query_params.get("tab_type")

    if not customer_id or not tab_type:
        return response_err(400, "customer_id와 tab_type은 필수값입니다.")

    try:
        queryset_map = {
            "voice": Consult.objects.filter(
                customer_id=customer_id, content_type="voice"
            ).order_by("-consult_date"),

            "active": Consult.objects.filter(
                customer_id=customer_id
            ).order_by("-consult_date"),
            
            "todo": TodoList.objects.filter(
                customer_id=customer_id
            ).order_by("-due_date"),
        }

        serializer_map = {
            "voice": ConsultSerializer,
            "active": ConsultSerializer,
            "todo": TodoSerializer,
        }

        queryset = queryset_map.get(tab_type)
        serializer_class = serializer_map.get(tab_type)

        serializer = serializer_class(queryset, many=True)

        return response_suc({"list": serializer.data})

    except Exception as e:
        return response_err(500, str(e))