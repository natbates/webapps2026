from django.urls import path
from .views import CustomLoginView
from django.contrib.auth import views as auth_views

app_name = 'login'

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
