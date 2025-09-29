from django.db import models
from pgvector.django import VectorField

class VectorFileInfo(models.Model):
    file_name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=1, choices=[('S','성공'), ('F','실패'), ('P','진행중')], default='P')
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField()

    def __str__(self):
        return self.file_name
    
    class Meta:
        db_table = "vector_file_info" 

class VectorFileDetail(models.Model):
    vec_info = models.ForeignKey(VectorFileInfo, on_delete=models.CASCADE, related_name="details")
    content = models.TextField(null=True)
    embedding = VectorField(dimensions=1536, null=True)  # OpenAI 임베딩 차원 예시
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "vector_file_detail" 


class VectorConsultData(models.Model):
    consult_id = models.IntegerField()
    content = models.TextField()
    embedding = VectorField(dimensions=1536, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
        
    class Meta:
        db_table = "vector_consult_data" 

class InsuranceTermsFile(models.Model):
    file_name = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=1, choices=[('S','성공'), ('F','실패'), ('P','진행중')], default='P')
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField()

    def __str__(self):
        return self.file_name
    
    class Meta:
        db_table = "insurance_terms_file" 

class InsuranceTermsFileDetail(models.Model):
    vec_info = models.ForeignKey(InsuranceTermsFile, on_delete=models.CASCADE, related_name="details")
    content = models.TextField(null=True)
    embedding = VectorField(dimensions=1536, null=True)  # OpenAI 임베딩 차원 예시
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "insurance_terms_file_detail" 