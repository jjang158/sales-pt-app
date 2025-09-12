import os, pdfplumber
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from .models import VectorFileInfo, VectorFileDetail
from django.db import transaction

PDF_DIR = "/home/ubuntu/sales-guide"

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

def chunk_text(text, chunk_size=1000, overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ".", " "]
    )
    return splitter.split_text(text)

def process_pdfs():
    files = [f for f in os.listdir(PDF_DIR) if f.endswith(".pdf")]

    for file_name in files:
        pdf_path = os.path.join(PDF_DIR, file_name)

        # 이미 처리된 파일은 skip
        if VectorFileInfo.objects.filter(file_name=file_name).exists():
            continue

        # vector_file_info에 상태 'P'로 저장
        file_info = VectorFileInfo.objects.create(file_name=file_name, status='P')

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
                    VectorFileDetail.objects.create(
                        vec_info=file_info,
                        content=chunk,
                        embedding=embedding
                    )

            # 성공 처리
            file_info.status = 'S'
            file_info.save()

        except Exception as e:
            # 실패 처리
            file_info.status = 'F'
            file_info.save()
            print(f"{file_name} 처리 실패: {str(e)}")
