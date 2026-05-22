from django.urls import path
from . import views


app_name = 'projects'

urlpatterns = [
    # === Список проектов (Главная страница) ===
    path('list/', views.project_list_view, name='project_list'),

    # === Детальная страница проекта ===
    path('<int:pk>/', views.project_detail_view, name='project_detail'),

    # === API действия над проектом (возвращают JSON) ===
    
    path('<int:pk>/complete/', views.project_complete_view, name='project_complete'),

    path('<int:pk>/toggle-participate/', views.toggle_participate_view, name='toggle_participate'),

    # === Управление проектом (Формы) ===

    path('create-project/', views.project_create_view, name='project_create'),

    path('<int:pk>/edit/', views.project_edit_view, name='project_edit'),

    path('<int:project_pk>/remove-participant/<int:participant_pk>/', 
     views.remove_participant_view, 
     name='remove_participant'),
]
