from django.db import connection
from ..common.vector_pool import get_conn, put_conn

def consult_search(query_embedding):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            # consult 검색
            cur.execute("""
                SELECT concat(to_char(c.consult_date, 'YYYY.MM.DD HH24:MI'), ' ', (select name from customer c2 where c.customer_id = c2.id)) as file_info, 
                       d.content, 'consult' AS type,
                       1 - (d.embedding <=> %s::vector) AS similarity
                 FROM vector_consult_data d
                    , consult c 
                WHERE d.consult_id = c.id
                ORDER BY d.embedding <=> %s::vector
                LIMIT 3
            """, (query_embedding, query_embedding))
            consult_results = cur.fetchall()
        return consult_results
    finally:
        put_conn(conn) 

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