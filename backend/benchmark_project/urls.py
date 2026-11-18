"""
URL configuration for benchmark_project.
"""
import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView
from django.views.static import serve

FRONTEND_DIR = os.path.normpath(os.path.join(settings.BASE_DIR, '..', 'frontend'))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('growth.urls')),
    re_path(r'^css/(?P<path>.*)$', serve, {'document_root': os.path.join(FRONTEND_DIR, 'css')}),
    re_path(r'^js/(?P<path>.*)$', serve, {'document_root': os.path.join(FRONTEND_DIR, 'js')}),
    path('', ensure_csrf_cookie(TemplateView.as_view(template_name='index.html')), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
