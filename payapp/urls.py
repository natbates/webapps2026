from django.urls import path
from . import views

app_name = 'payapp'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('transactions/', views.transactions, name='transactions'),
    path('requests/', views.requests_list, name='requests'),
    path('make/', views.make_payment, name='make_payment'),
    path('request/', views.request_payment, name='request_payment'),
    path('request/<uuid:pk>/cancel/', views.cancel_request, name='cancel_request'),
    path('request/<uuid:pk>/accept/', views.accept_request, name='accept_request'),
    path('request/<uuid:pk>/reject/', views.reject_request, name='reject_request'),
]
