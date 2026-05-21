from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    """
    Форма для создания и редактирования проекта
    Используется на странице /projects/create-project/ и /projects/<id>/edit/
    """
    class Meta:
        model = Project
        # Поля, которые пользователь может заполнять вручную
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Например: Приложение для отслеживания привычек',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Расскажите, что должен делать проект..',
                'class': 'form-control'
            }),
            'github_url': forms.URLInput(attrs={
                'placeholder': 'https://github.com/username/project-name',
                'class': 'form-control'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_github_url(self):
        """
        Валидация ссылки на GitHub
        Проверяет, что ссылка ведёт именно на домен github.com
        """
        url = self.cleaned_data.get('github_url', '').strip()
        
        if url:
            # Проверка протокола
            if not url.lower().startswith(('http://', 'https://')):
                raise forms.ValidationError('Ссылка должна начинаться с http:// или https://')
            
            # Проверка домена
            if 'github.com' not in url.lower():
                raise forms.ValidationError('Ссылка должна вести на репозиторий GitHub (домен github.com)')
                
        return url