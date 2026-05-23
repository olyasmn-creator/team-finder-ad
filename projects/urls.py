from django.urls import path
from . import views


app_name = 'projects'

urlpatterns = [
    path('list/', views.project_list_view, name='project_list'),
    path('<int:pk>/', views.project_detail_view, name='project_detail'),
    path('<int:pk>/complete/', views.project_complete_view, name='project_complete'),
    path('<int:pk>/toggle-participate/', views.toggle_participate_view, name='toggle_participate'),
    path('create-project/', views.project_create_view, name='project_create'),
    path('<int:pk>/edit/', views.project_edit_view, name='project_edit'),
    path('<int:project_pk>/remove-participant/<int:participant_pk>/', 
         views.remove_participant_view, 
         name='remove_participant'),
]
