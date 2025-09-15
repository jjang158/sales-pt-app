from django.db import models

class Customer(models.Model):
    id = models.AutoField(primary_key=True)  # INT / PK, AUTO_INCREMENT / 고객 ID
    name = models.CharField(max_length=100)  # VARCHAR(100) / NOT NULL / 고객 이름
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True)  # VARCHAR(20) / UNIQUE / 연락처
    email = models.CharField(max_length=100, null=True)  # VARCHAR(100) / NULL / 이메일
    address = models.CharField(max_length=200, null=True)  # VARCHAR(200) / NULL / 주소
    remark = models.TextField(null=True, blank=True)  # TEXT / NULL / 비고
    created_at = models.DateTimeField()  # TIMESTAMP / DEFAULT now() / 등록일
    updated_at = models.DateTimeField()  # TIMESTAMP / DEFAULT now() / 수정일

    class Meta:
        db_table = 'customer'
        managed = False


class Todo_list(models.Model):
    id= models.AutoField(primary_key=True) # INT / PK,AUTO_INCREMENT / 고유 ID
    customer_id=models.IntegerField(null=True) # INT / NULL,FK > customir.id / 상담고객
    due_date= models.DateTimeField(blank=True, null=True) # Timestamp / NULL / 마감일
    title= models.CharField(max_length=200) # VARCHAR(200) / Not null / 할일 제목
    description= models.TextField(null=True) # Text / Null / 상세 설명
    is_completed= models.BooleanField(default=False) # BOOLEAN / DEFAULT FALSE / 완료 여부
    created_at= models.DateTimeField() # Timestamp / Default now() / 생성일

    class Meta:
        db_table = 'todo_list'
        managed = False

class Consult(models.Model):
    # 상담 정보 , Master
    id= models.AutoField(primary_key=True) #INT / PK,Auto_INCREMENT / 상담 ID
    consult_date= models.DateTimeField() # Timestamp / Default now() / 상담 일시
    customer_id= models.IntegerField() # INT / Not Null, FK > customer.id / 상담 고객
    consult_text= models.TextField() # Text / Not null / 상담 내용

    class Meta:
        db_table = 'consult'
        managed = False

class Consult_stage(models.Model):
    id= models.AutoField(primary_key=True) # INT / PK,Auto_Increment / 상담단계 ID
    consult_id= models.IntegerField() # INT / FK > consult_id / 상담 정보 ID(consult.id)
    stage_meta_id= models.IntegerField() # INT / FK > sales_stage_meta.id / 영업 단계 ID(sales_stage_meta.id)
    stage_name= models.CharField(max_length=50) # VARCHAR(50) / Not null / 단계명 (스냅샷 저장)
    created_at= models.DateTimeField() # Timestamp / Default now() / 생성 시각

    class Meta:
        db_table = 'consult_stage'
        managed = False