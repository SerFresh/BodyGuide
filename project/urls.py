from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('guide/', views.index),
    path('', views.upload_basic),
    path('details/', views.detail),
    path('members/', views.members)
]

urlpatterns += static(settings.MEDIA_URL , document_root=settings.MEDIA_ROOT)
