import os
from psycopg2.pool import ThreadedConnectionPool
from pgvector.psycopg2 import register_vector

PG_DSN = (
    f"host={os.getenv('DB_HOST', '127.0.0.1')} "
    f"port={os.getenv('DB_PORT', '5432')} "
    f"dbname={os.getenv('DB_NAME', 'postgres')} "
    f"user={os.getenv('DB_USER', 'postgres')} "
    f"password={os.getenv('DB_PASSWORD', '')}"
)

# 커넥션 풀 초기화
POOL = ThreadedConnectionPool(minconn=1, maxconn=10, dsn=PG_DSN)

# 벡터 타입 등록 (최초 1회만)
conn = POOL.getconn()
conn.autocommit = True
register_vector(conn)
POOL.putconn(conn)

def get_conn():
    conn = POOL.getconn()
    conn.autocommit = True
    return conn

def put_conn(conn):
    """커넥션을 풀에 반환"""
    POOL.putconn(conn)
