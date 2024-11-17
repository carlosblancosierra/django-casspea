from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import Product
from .serializers import ProductSerializer

class ProductListView(ListAPIView):
    queryset = Product.objects.active()
    serializer_class = ProductSerializer

class ProductDetailView(RetrieveAPIView):
    lookup_field = 'slug'
    queryset = Product.objects.active()
    serializer_class = ProductSerializer
