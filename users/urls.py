from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    # === Авторизация и регистрация ===
    
    path('register/', views.register_view, name='register'),
    
    path('login/', views.login_view, name='login'),
    
    path('logout/', views.logout_view, name='logout'),
    
    path('change-password/', views.password_change_view, name='password_change'),
    
    # === Профиль пользователя ===
    
    path('<int:pk>/', views.profile_view, name='profile'),
    
    path('<int:pk>/edit/', views.profile_edit_view, name='profile_edit'),
    
    # === Список пользователей с фильтрацией ===
    
    path('list/', views.user_list_view, name='user_list'),
    
    # === API для работы с навыками ===
    
    path('skills/', views.skill_search_api, name='skill_search'),
    
    path('<int:user_id>/skills/add/', views.skill_add_api, name='skill_add'),
    
    path('<int:user_id>/skills/<int:skill_id>/remove/', views.skill_remove_api, name='skill_remove'),
]
