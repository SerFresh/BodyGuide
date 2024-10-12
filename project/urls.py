from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload/', views.index),
    path('',views.upload_basic),
]

urlpatterns += static(settings.MEDIA_URL , document_root=settings.MEDIA_ROOT)