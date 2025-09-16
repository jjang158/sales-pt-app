from rest_framework import serializers
from .models import SalesStageMeta

class SalesStageMetaSerializer(serializers.ModelSerializer):
    child_list = serializers.SerializerMethodField()

    class Meta:
        model = SalesStageMeta
        fields = ("id", "name", "order", "parent_id", "child_list")

    def get_child_list(self, obj):
        children = obj.child_list.all().order_by("order")
        return SalesStageMetaSerializer(children, many=True).data
