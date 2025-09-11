from django.db import models

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