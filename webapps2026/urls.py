"""
URL configuration for webapps2026 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('login/', include(('login.urls', 'login'), namespace='login')),
    path('register/login/', RedirectView.as_view(url='/login/', permanent=False)),
    path('admin-dashboard/', include(('admindashboard.urls', 'admindashboard'), namespace='admindashboard')),
    path('register/', include('register.urls')),
    path('payments/', include('payapp.urls')),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    static_root = getattr(settings, 'STATIC_ROOT', None)
    if static_root:
        urlpatterns += static(settings.STATIC_URL, document_root=static_root)
