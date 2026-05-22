from django.urls import path
from . import views

# Пространство имён для приложения projects
# Позволяет обращаться к URL как 'projects:list', 'projects:detail' и тд
app_name = 'projects'

urlpatterns = [
    # === Список проектов (Главная страница) ===
    # Пагинация по 12 проектов, сортировка по дате (новые сверху)
    path('list/', views.project_list_view, name='project_list'),

    # === Детальная страница проекта ===
    # Отображение информации, участников, кнопок управления
    path('<int:pk>/', views.project_detail_view, name='project_detail'),

    # === API действия над проектом (возвращают JSON) ===
    
    # Завершить проект (только для владельца)
    # Метод: POST
    path('<int:pk>/complete/', views.project_complete_view, name='project_complete'),

    # Присоединиться к проекту / Покинуть проект (для гостей)
    # Метод: POST
    path('<int:pk>/toggle-participate/', views.toggle_participate_view, name='toggle_participate'),

    # === Управление проектом (Формы) ===

    # Создать новый проект
    path('create-project/', views.project_create_view, name='project_create'),

    # Редактировать существующий проект
    path('<int:pk>/edit/', views.project_edit_view, name='project_edit'),

    path('<int:project_pk>/remove-participant/<int:participant_pk>/', 
     views.remove_participant_view, 
     name='remove_participant'),
]
