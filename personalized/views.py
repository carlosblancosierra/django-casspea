from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ChocolateTemplate
from .serializers import ChocolateTemplateDetailSerializer


class TemplateListView(APIView):
    def get(self, request, *args, **kwargs):
        templates = ChocolateTemplate.objects.all()
        serializer = ChocolateTemplateDetailSerializer(templates, many=True)
        return Response(serializer.data)


class TemplateDetailView(APIView):
    def get(self, request, slug, *args, **kwargs):
        try:
            template = ChocolateTemplate.objects.get(slug=slug)
        except ChocolateTemplate.DoesNotExist:
            return Response({"error": "Template not found"}, status=404)

        serializer = ChocolateTemplateDetailSerializer(template)
        return Response(serializer.data)