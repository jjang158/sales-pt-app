from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
import json
from django.http import JsonResponse
from .models import Todo_list

# Todo List 조회 API
@api_view(['GET'])
def todo(request, id=None):
    cursor = connection.cursor()
    try:
        sql = "SELECT id, customer_id, due_date, title, description, is_completed, created_at FROM todo_list WHERE 1=1"
        
        if id:
            sql += f" AND id = {id}"
        
        # customer_id 필터
        customer_id = request.GET.get('customer_id')
        if customer_id:
            try:
                customer_id = int(customer_id)
                sql += f" AND customer_id = {customer_id}"
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'status': 400,
                    'message': 'customer_id는 정수여야 합니다.',
                    'data': []
                })
        
        # is_completed 필터
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
            
        return JsonResponse({
            'success': True,
            'status': 200,
            'message': 'Todo List 조회 성공',
            'data': todos
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'status': 500,
            'message': f'오류: {str(e)}',
            'data': []
        })
    finally:
        cursor.close()