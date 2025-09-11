from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection

@api_view(['POST'])
def save_consult(request):
    try:
        # Request Body에서 데이터 추출
        customer_id = request.data.get('customer_id')
        consult_text = request.data.get('consult_text')
        stages = request.data.get('stages', [])
        
        # 필수 필드 검증
        if not customer_id:
            return Response({
                'status': 400,
                'message': 'customer_id는 필수입니다.',
                'data': {}
            })
            
        if not consult_text:
            return Response({
                'status': 400,
                'message': 'consult_text는 필수입니다.',
                'data': {}
            })
        
        with connection.cursor() as cursor:
            # 1. consult 테이블에 데이터 저장
            cursor.execute("""
                INSERT INTO consult (customer_id, consult_text, consult_date)
                VALUES (%s, %s, NOW())
            """, [customer_id, consult_text])
            
            # 생성된 consult_id 가져오기
            consult_id = cursor.lastrowid
            
            # 2. stages 배열 처리 - 여러 개 저장
            for stage in stages:
                stage_meta_id = stage.get('stage_meta_id')
                stage_name = stage.get('stage_name')
                
                if stage_meta_id and stage_name:
                    cursor.execute("""
                        INSERT INTO consult_stage (consult_id, stage_meta_id, stage_name, created_at)
                        VALUES (%s, %s, %s, NOW())
                    """, [consult_id, stage_meta_id, stage_name])
        
        return Response({
            'status': 200,
            'message': 'Success',
            'data': {}
        })
        
    except Exception as e:
        return Response({
            'status': 500,
            'message': f'저장 중 오류가 발생했습니다: {str(e)}',
            'data': {}
        })