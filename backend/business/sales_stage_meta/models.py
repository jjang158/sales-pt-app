from django.db import models

class SalesStageMeta(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=False)
    description = models.TextField(null=True, blank=True)
    order = models.IntegerField(default=0)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="child_list"
    )

    class Meta:
        db_table = "sales_stage_meta"
        ordering = ["order"]

    def __str__(self):
        return self.name
