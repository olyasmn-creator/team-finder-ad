from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Настройка администрирования проектов"""
    
    # Поля для отображения в списке
    list_display = ('name', 'owner', 'status', 'created_at', 'github_url')
    
    # Поля для фильтрации в правой панели
    list_filter = ('status', 'created_at', 'owner')
    
    # Поля для поиска
    search_fields = ('name', 'description', 'owner__name', 'owner__surname')
    
    # Поля для группировки по датам
    date_hierarchy = 'created_at'
    
    # Поля, доступные для редактирования в списке
    list_editable = ('status',)
    
    # Количество элементов на странице
    list_per_page = 20
    
    # Поля, которые будут отображаться в форме создания/редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'owner', 'status')
        }),
        ('Дополнительно', {
            'fields': ('github_url', 'participants'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('participants',)
