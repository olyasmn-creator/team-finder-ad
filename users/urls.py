from django.urls import path
from . import views

# Пространство имён для приложения users
# Позволяет обращаться к URL как 'users:register', 'users:profile' и тд
app_name = 'users'

urlpatterns = [
    # === Авторизация и регистрация ===
    
    # Страница регистрации нового пользователя
    path('register/', views.register_view, name='register'),
    
    # Страница входа в аккаунт
    path('login/', views.login_view, name='login'),
    
    # Выход из аккаунта (только GET-запрос)
    path('logout/', views.logout_view, name='logout'),
    
    # Страница смены пароля (только для авторизованных)
    path('change-password/', views.password_change_view, name='password_change'),
    
    # === Профиль пользователя ===
    
    # Публичный профиль: /users/5/
    path('<int:pk>/', views.profile_view, name='profile'),
    
    # Редактирование своего профиля: /users/5/edit/
    path('<int:pk>/edit/', views.profile_edit_view, name='profile_edit'),
    
    # === Список пользователей с фильтрацией ===
    
    # Список всех участников: /users/list/?skill=Python
    path('list/', views.user_list_view, name='user_list'),
    
    # === API для работы с навыками ===
    # Эти эндпоинты возвращают JSON
    
    # Поиск навыков для автодополнения: /users/skills/?q=py
    path('skills/', views.skill_search_api, name='skill_search'),
    
    # Добавить навык пользователю: POST /users/5/skills/add/
    path('<int:user_id>/skills/add/', views.skill_add_api, name='skill_add'),
    
    # Удалить навык у пользователя: POST /users/5/skills/3/remove/
    path('<int:user_id>/skills/<int:skill_id>/remove/', views.skill_remove_api, name='skill_remove'),
]
