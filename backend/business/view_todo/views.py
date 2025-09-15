from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection
import json
from django.http import JsonResponse
from .models import Todo_list
from ..common.response_format import response_suc, response_err

# Todo List 조회 API
@api_view(['GET'])
def todo(request, id=None):
    cursor = connection.cursor()
    try:
        sql = """
        SELECT 
            t.id, 
            t.customer_id, 
            c.name as customer_name,
            t.due_date, 
            t.title, 
            t.description, 
            t.is_completed, 
            t.created_at 
        FROM todo_list t
        LEFT JOIN customer c ON t.customer_id = c.id
        WHERE 1=1
        """
        
        if id:
            sql += f" AND id = {id}"
        
        # customer_id 필터
        customer_id = request.GET.get('customer_id')
        if customer_id:
            try:
                customer_id = int(customer_id)
                sql += f" AND customer_id = {customer_id}"
            except ValueError:
                return response_err(400,'customer_id는 정수여야 합니다.')
        
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
                'customer_name':row[2],
                'due_date': row[3].isoformat() if row[3] else None,
                'title': row[4],
                'description': row[5],
                'is_completed': row[6],
                'created_at': row[7].isoformat() if row[7] else None
            })
            
        return response_suc(todos)
        
    except Exception as e:
        return response_err(500,f'오류: {str(e)}')
    finally:
        cursor.close()