from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from .models import User
import re
from projects.forms import GitHubUrlMixin


class RegisterForm(forms.ModelForm):
    """
    Форма регистрации нового пользователя
    Содержит обязательные поля: name, surname, email, password
    """
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Придумайте пароль'})
    )
    
    # Дополнительное поле для валидации
    phone = forms.CharField(
        label='Телефон',
        max_length=12,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+79991234567'})
    )

    class Meta:
        model = User
        # Поля модели, которые будут в форме
        fields = ['name', 'surname', 'email', 'password']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ольга'}),
            'surname': forms.TextInput(attrs={'placeholder': 'Симонова'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@example.com'}),
        }

    def clean_phone(self):
        """
        Валидация номера телефона
        Разрешены форматы: 8XXXXXXXXXX или +7XXXXXXXXXX
        Приводит к единому формату +7..
        """
        phone = self.cleaned_data.get('phone', '')
    
        # Если поле пустое - возвращаем пустую строку (телефон не обязателен)
        if not phone:
            return ''
    
        # Убираем все нецифровые символы
        clean_phone = re.sub(r'\D', '', phone)
        
        # Проверка длины и формата
        if len(clean_phone) != 11:
            raise forms.ValidationError('Номер телефона должен содержать 11 цифр.')
        
        # Проверка префикса (8 или 7)
        if clean_phone.startswith('8'):
            clean_phone = '7' + clean_phone[1:]
        elif not clean_phone.startswith('7'):
            raise forms.ValidationError('Номер должен начинаться с 8 или +7.')
        
        # Формируем итоговый номер с плюсом
        final_phone = '+' + clean_phone
        
        # Проверка уникальности номера в базе
        if User.objects.filter(phone=final_phone).exists():
            raise forms.ValidationError('Пользователь с таким номером телефона уже существует.')
            
        return final_phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            user.phone = phone
        else:
            user.phone = None
        
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """
    Форма входа в систему
    Наследуемся от стандартной AuthenticationForm, но меняем поле username на email
    """
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'autofocus': True, 'placeholder': 'Ваш email'})
    )
    password = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Ваш пароль'})
    )


class ProfileEditForm(GitHubUrlMixin, forms.ModelForm):
    """
    Форма редактирования профиля пользователя
    Позволяет изменить name, surname, avatar, about, phone, github_url
    """
    
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Расскажите о себе'}),
        }

    def clean_phone(self):
        """
        Та же валидация телефона, что и при регистрации
        """
        phone = self.cleaned_data.get('phone', '')
        if not phone:
            return phone
            
        clean_phone = re.sub(r'\D', '', phone)
        
        if len(clean_phone) != 11:
            raise forms.ValidationError('Неверный формат номера.')
            
        if clean_phone.startswith('8'):
            clean_phone = '7' + clean_phone[1:]
        elif not clean_phone.startswith('7'):
            raise forms.ValidationError('Номер должен начинаться с 8 или +7.')
            
        final_phone = '+' + clean_phone
        
        # Проверка уникальности, исключая текущего пользователя
        if User.objects.filter(phone=final_phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Этот номер телефона уже используется.')
            
        return final_phone


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Кастомная форма смены пароля
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Можно добавить placeholder'ы, если нужно
        for field_name in ['old_password', 'new_password1', 'new_password2']:
            self.fields[field_name].widget.attrs.update({'placeholder': 'Введите пароль'})
