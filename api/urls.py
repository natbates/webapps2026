from django.urls import path
from .views import conversion_view

app_name = 'api'

urlpatterns = [
    path('conversion/<str:from_curr>/<str:to_curr>/<str:amount>/', conversion_view, name='conversion'),
]
