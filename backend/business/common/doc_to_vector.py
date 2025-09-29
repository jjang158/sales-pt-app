import os, pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from django.db import transaction

# pdf 파일 텍스트 추출
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

# 청킹 작업(텍스트 쪼개기)
def chunk_text(text, chunk_size=1000, overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    return splitter.split_text(text)


# 지정된 디렉터리 내 PDF 파일들을 순차적으로 벡터화하여 DB에 저장하는 함수.
# Args:
#     pdf_dir (str): PDF 파일들이 위치한 디렉터리 경로
#     vector_info (Model): 벡터 파일 마스터 정보 저장용 모델 (예: vector_file_info)
#     vector_detail (Model): 벡터화된 텍스트(청크 단위) 저장용 모델 (예: vector_file_detail)
# Process:
#     1. 지정된 폴더 내의 PDF 파일 목록을 조회
#     2. 이미 벡터화 완료(status='S')된 파일은 스킵
#     3. 새로운 파일은 `process_pdfs` 함수를 호출하여 처리
#     4. 처리 성공/실패에 따른 카운트 집계
# Returns:
#     tuple: (총 파일 개수, 성공적으로 벡터화된 파일 개수)
def guide_pdf_vectorizing(pdf_dir, vector_info, vector_detail, user_id=None):
    files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    suc_count = 0

    for file_name in files:
        pdf_path = os.path.join(pdf_dir, file_name)

        # 이미 처리된 파일은 skip
        if vector_info.objects.filter(file_name=file_name).filter(status='S').exists():
            continue

        suc_count = process_pdfs(pdf_path, file_name, vector_info, vector_detail, user_id)

    return len(files), suc_count


# 단일 PDF 파일을 벡터화하여 DB에 저장하는 함수.
# Args:
#     pdf_path (str): PDF 파일 전체 경로
#     file_name (str): PDF 파일 이름
#     vector_info (Model): 벡터 파일 마스터 정보 저장용 모델 (예: vector_file_info)
#     vector_detail (Model): 벡터화된 텍스트(청크 단위) 저장용 모델 (예: vector_file_detail)
# Process:
#     1. `vector_file_info` 테이블에 상태 'P'(진행중)으로 마스터 정보 저장
#     2. PDF 파일 텍스트 추출
#     3. 텍스트를 청크 단위로 분리
#     4. 각 청크에 대해 OpenAI 임베딩을 생성
#     5. `vector_file_detail` 테이블에 벡터(임베딩) 및 원문 청크 저장
#     6. 성공 시 마스터 상태를 'S'(성공)으로 업데이트
#     7. 실패 시 마스터 상태를 'F'(실패)로 업데이트
# Returns:
#     int: 성공적으로 처리된 파일 개수 (성공 시 1, 실패 시 0)
def process_pdfs(pdf_path, file_name, vector_info, vector_detail, user_id):
    suc_count=0 # 변수초기화
    # vector_file_info에 상태 'P'로 저장
    file_info = vector_info.objects.create(file_name=file_name, status='P', user_id=user_id ) #user_id 추가

    try:
        # 1. PDF 텍스트 추출
        text = extract_text_from_pdf(pdf_path)

        # 2. 청킹
        chunks = chunk_text(text)

        # 3. 임베딩 생성
        embedder = OpenAIEmbeddings()
        with transaction.atomic():
            for chunk in chunks:
                embedding = embedder.embed_query(chunk)
                vector_detail.objects.create(
                    vec_info=file_info,
                    content=chunk,
                    embedding=embedding
                )

        # 성공 처리
        suc_count = suc_count+1
        file_info.status = 'S'
        file_info.save()
        return suc_count

    except Exception as e:
        # 실패 처리
        file_info.status = 'F'
        file_info.save()
        print(f"{file_name} 처리 실패: {str(e)}")
        return 0