from rest_framework import serializers
from .models import Consult, TodoList, ConsultStage

class ConsultStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultStage
        fields = ["stage_name"]

class ConsultSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    content = serializers.CharField(source="consult_text")
    consult_stage = ConsultStageSerializer(source="stages", many=True)

    class Meta:
        model = Consult
        fields = ["content_type", "title", "content", "consult_stage"]

    def get_title(self, obj):
        return "" 

class TodoSerializer(serializers.ModelSerializer):
    content_type = serializers.SerializerMethodField()
    content = serializers.CharField(source="description")
    consult_stage = serializers.SerializerMethodField()

    class Meta:
        model = TodoList
        fields = ["content_type", "title", "content", "consult_stage"]

    def get_content_type(self, obj):
        return "todo"

    def get_consult_stage(self, obj):
        return [] 
