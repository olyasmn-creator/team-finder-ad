from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Настройка администрирования проектов"""
    
    list_display = ('name', 'owner', 'status', 'created_at', 'github_url')
    list_filter = ('status', 'created_at', 'owner')
    search_fields = ('name', 'description', 'owner__name', 'owner__surname')
    date_hierarchy = 'created_at'
    list_editable = ('status',)
    list_per_page = 20
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
