from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Админ-панель Django (доступна только для is_staff=True)
    path('admin/', admin.site.urls),
    
    # === Перенаправление с корня сайта ===
    # При заходе на '/' пользователь попадает на список проектов
    path('', lambda request: redirect('projects:project_list')),
    
    # === Подключение маршрутов приложений ===
    # Все URL, начинающиеся с 'users/', будут обрабатываться в users/urls.py
    path('users/', include('users.urls')),
    
    # Все URL, начинающиеся с 'projects/', будут обрабатываться в projects/urls.py
    path('projects/', include('projects.urls')),
]

# === Раздача медиа-файлов в режиме отладки ===
# В продакшене это должен делать веб-сервер (Nginx, Apache)
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,  # URL-префикс для медиа: '/media/'
        document_root=settings.MEDIA_ROOT  # Папка на диске: '/path/to/media'
    )