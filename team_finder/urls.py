from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # === Перенаправление с корня сайта ===
    path('', lambda request: redirect('projects:project_list')),
    
    # === Подключение маршрутов приложений ===
    path('users/', include('users.urls')),
    
    path('projects/', include('projects.urls')),
]

# === Раздача медиа-файлов в режиме отладки ===
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,  # URL-префикс для медиа: '/media/'
        document_root=settings.MEDIA_ROOT  # Папка на диске: '/path/to/media'
    )
