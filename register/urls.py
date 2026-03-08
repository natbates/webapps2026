from django.urls import path
from . import views

app_name = 'register'

urlpatterns = [
    # registration page
    path('', views.register_view, name='register'),
    # local login route using our custom LoginView with better feedback
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    # admin-style dashboard (project requirement: do not rely on Django admin site)
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
