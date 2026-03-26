from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔥 ВАЖНО
    path('accounts/', include('allauth.urls')),

    path('', include('main.urls')),
]