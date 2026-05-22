from django import forms
from .models import Project


GITHUB_DOMAIN = 'github.com'
GITHUB_URL_PROTOCOLS = ('http://', 'https://')


class GitHubUrlMixin:
    """
    Миксин для валидации ссылки на GitHub.
    Можно использовать в любых формах, где есть поле github_url.
    """
    def clean_github_url(self):
        """
        Валидация ссылки на GitHub.
        Проверяет, что ссылка ведёт именно на домен github.com.
        """
        url = self.cleaned_data.get('github_url', '').strip()
        
        if url:
            if not url.lower().startswith(GITHUB_URL_PROTOCOLS):
                raise forms.ValidationError(
                    f'Ссылка должна начинаться с http:// или https://'
                )
            
            if GITHUB_DOMAIN not in url.lower():
                raise forms.ValidationError(
                    f'Ссылка должна вести на репозиторий GitHub (домен {GITHUB_DOMAIN})'
                )
                
        return url


class ProjectForm(GitHubUrlMixin, forms.ModelForm):
    """
    Форма для создания и редактирования проекта.
    Используется на странице /projects/create-project/ и /projects/<id>/edit/
    """
    class Meta:
        model = Project
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
