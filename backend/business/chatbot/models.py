from django.db import models
from pgvector.django import VectorField

class VectorFileInfo(models.Model):
    file_name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=1, choices=[('S','성공'), ('F','실패'), ('P','진행중')], default='P')
    created_at = models.DateTimeField(auto_now_add=True)

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
