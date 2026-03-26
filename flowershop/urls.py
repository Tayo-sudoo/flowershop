from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔥 ДОБАВЬ ЭТО (ОЧЕНЬ ВАЖНО)
    path('accounts/', include('allauth.urls')),

    path('', include('main.urls')),
]

# MEDIA (фото товаров)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# STATIC (css, js)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)