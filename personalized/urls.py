from django.urls import path
from .views import TemplateListView, TemplateDetailView

urlpatterns = [
    path('templates/', TemplateListView.as_view(), name='template-list'),
    path('templates/<slug:slug>/', TemplateDetailView.as_view(), name='template-detail'),
]
