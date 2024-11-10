from django.shortcuts import render
from rest_framework.generics import ListAPIView
from flavours.models import Flavour
from flavours.serializers import FlavourSerializer

# Create your views here.
class FlavourListView(ListAPIView):
    queryset = Flavour.objects.active()
    serializer_class = FlavourSerializer
