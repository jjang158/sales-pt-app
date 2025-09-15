from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=200)
    class Meta:
        db_table = "customer"
        verbose_name = "고객"


class Consult(models.Model):
    consult_date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    consult_text = models.TextField()
    content_type = models.CharField(max_length=10)  # voice, text
    is_vectorized = models.BooleanField(default=False)
    class Meta:
        db_table = "consult"
        verbose_name = "상담 정보"


class TodoList(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    due_date = models.DateTimeField(null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "todo_list"
        verbose_name = "할 일"


class ConsultStage(models.Model):
    consult = models.ForeignKey(Consult, on_delete=models.CASCADE, related_name="stages")
    stage_meta_id = models.IntegerField()
    stage_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "consult_stage"
        verbose_name = "상담 단계"
