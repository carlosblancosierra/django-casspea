
from django.urls import path
from flavours.views import FlavourListView

flavours_urls = [
    path('', FlavourListView.as_view(), name='flavour-list'),
]
