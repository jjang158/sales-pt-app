from rest_framework.views import APIView
from .models import SalesStageMeta
from .serializers import SalesStageMetaSerializer
from ..common.response_format import response_suc, response_err

class SalesStageMetaView(APIView):
    def get(self, request):
        try:
            queryset = SalesStageMeta.objects.filter(parent__isnull=True).order_by("order")
            serializer = SalesStageMetaSerializer(queryset, many=True)

            return response_suc({"list": serializer.data })

        except Exception as e:
            return response_err(str(e), status_code=500)
