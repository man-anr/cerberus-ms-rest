from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

@extend_schema(tags=["Meta"], responses={200: None})
class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok"})