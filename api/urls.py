from django.urls import path
from .views import ConversionView

app_name = 'api'

urlpatterns = [
    path('conversion/<str:from_curr>/<str:to_curr>/<str:amount>/', ConversionView.as_view(), name='conversion'),
]
