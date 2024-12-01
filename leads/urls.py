from django.urls import path
from .views import SubscribeNewsletterView

app_name = 'mails'

urlpatterns = [
    path('subscribe/', SubscribeNewsletterView.as_view(), name='subscribe'),
]
