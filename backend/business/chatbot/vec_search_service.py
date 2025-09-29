from django.db import connection
from ..common.vector_pool import get_conn, put_conn

# 고객상담 백터 정보 조회
def consult_search(query_embedding):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # consult 검색
            query = """
            SELECT 
                concat(to_char(c.consult_date, 'YYYY.MM.DD HH24:MI'), ' ', 
                    (select name from customer c2 where c.customer_id = c2.id)) as file_info, 
                d.content, 
                'consult' AS type,
                (
                    (1 - (d.embedding <=> %s::vector)) * 0.7
                    +
                    (1 / (1 + EXTRACT(EPOCH FROM (now() - c.consult_date)) / 86400)) * 0.3
                ) AS score
            FROM vector_consult_data d
            JOIN consult c ON d.consult_id = c.id
            ORDER BY score DESC
            LIMIT 3;
            """
            cur.execute(query, (query_embedding,))
            consult_results = cur.fetchall()
        return consult_results
    finally:
        put_conn(conn) 

# 영업 가이드 정보 조회
def document_search(query_embedding):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # document 검색
            cur.execute("""
                SELECT vfi.file_name as file_info, vfd.content, 'document' AS type,
                       1 - (vfd.embedding <=> %s::vector) AS similarity
                FROM vector_file_info vfi 
                   , vector_file_detail vfd 
                WHERE vfi.id = vfd.vec_info_id
                ORDER BY vfd.embedding <=> %s::vector
                LIMIT 3
            """, (query_embedding, query_embedding))
            doc_results = cur.fetchall()
        return doc_results
    finally:
        put_conn(conn) 
        

# 상품설명 정보 조회
def insurance_search(query_embedding, user_id):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # document 검색
            cur.execute("""
                SELECT vfi.file_name as file_info, vfd.content, 'document' AS type,
                       1 - (vfd.embedding <=> %s::vector) AS similarity
                FROM insurance_terms_file vfi 
                   , insurance_terms_file_detail vfd 
                WHERE vfi.id = vfd.vec_info_id
                  AND vfi.user_id = %s
                ORDER BY vfd.embedding <=> %s::vector
                LIMIT 3
            """, (query_embedding, user_id, query_embedding))
            doc_results = cur.fetchall()
        return doc_results
    finally:
        put_conn(conn) 