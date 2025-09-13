from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
<<<<<<< Updated upstream
from common.response_format import response_suc, response_err
=======
from ..common.response_format import response_suc, response_err
from .openaiservice import analyze_consult_text 
import json
from django.http import JsonResponse
from .models import Todo_list
>>>>>>> Stashed changes

@api_view(['POST'])
def save_consult(request):
    try:
        customer_id = request.data.get('customer_id')
        consult_text = request.data.get('consult_text')
        stages = request.data.get('stages', [])
        
        if not customer_id:
            return response_err(400, 'customer_id는 필수입니다.')
            
        if not consult_text:
            return Response({
                'status': 400,
                'message': 'consult_text는 필수입니다.',
                'data': {}
            })
        
        if not stages:
            return Response({
                'status': 400,
                'message': 'stages는 최소 1개 이상이어야 합니다.',
                'data': {}
            })
        
        cursor = connection.cursor()
        

        # stage 검증
        for stage in stages:
            stage_meta_id= stage.get('stage_meta_id')
            stage_name= stage.get('stage_name')
                
            if not stage_meta_id:
                return Response({
                    'status': 400,
                    'message': f'stage_meta_id는 필수입니다.',
                    'data': {}
                })
        
            if not stage_name:
                return Response({
                    'status': 400,
                    'message': f'stage_name은 필수입니다.',
                    'data': {}
                })
                
            if not isinstance(stage_meta_id, int) or stage_meta_id <= 0:
                return Response({
                    'status': 400,
                    'message': f'stage_meta_id는 양수여야 합니다.',
                    'data': {}
                })

        cursor.execute(
            """INSERT INTO consult (customer_id, consult_text, consult_date)
            VALUES (%s, %s, NOW()) RETURNING id""", [customer_id, consult_text])
        
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
        return Response({
            'status': 500,
            'message': f'저장 중 오류가 발생했습니다: {str(e)}',
            'data': {}
        })