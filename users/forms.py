import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm

from .models import User
from projects.forms import GitHubUrlMixin


class PhoneValidationMixin:
    """Миксин для валидации номера телефона"""
    
    def clean_phone(self):
        """
        Валидация номера телефона
        Разрешены форматы: 8XXXXXXXXXX или +7XXXXXXXXXX
        Приводит к единому формату +7..
        """
        phone = self.cleaned_data.get('phone', '')
    
        if not phone:
            return ''
    
        clean_phone = re.sub(r'\D', '', phone)
        
        if len(clean_phone) != 11:
            raise forms.ValidationError('Номер телефона должен содержать 11 цифр.')
        
        if clean_phone.startswith('8'):
            clean_phone = '7' + clean_phone[1:]
        elif not clean_phone.startswith('7'):
            raise forms.ValidationError('Номер должен начинаться с 8 или +7.')
        
        final_phone = '+' + clean_phone
        
        if hasattr(self, 'instance') and self.instance.pk:
            if User.objects.filter(phone=final_phone).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Этот номер телефона уже используется.')
        else:
            if User.objects.filter(phone=final_phone).exists():
                raise forms.ValidationError('Пользователь с таким номером телефона уже существует.')
            
        return final_phone


class RegisterForm(PhoneValidationMixin, forms.ModelForm):
    """
    Форма регистрации нового пользователя
    Содержит обязательные поля: name, surname, email, password
    """
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Придумайте пароль'})
    )
    
    phone = forms.CharField(
        label='Телефон',
        max_length=12,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '+79991234567'})
    )

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ольга'}),
            'surname': forms.TextInput(attrs={'placeholder': 'Симонова'}),
            'email': forms.EmailInput(attrs={'placeholder': 'email@example.com'}),
        }

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


class ProfileEditForm(PhoneValidationMixin, GitHubUrlMixin, forms.ModelForm):
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


class PasswordChangeForm(PasswordChangeForm):
    """
    Форма смены пароля
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['old_password', 'new_password1', 'new_password2']:
            self.fields[field_name].widget.attrs.update({'placeholder': 'Введите пароль'})
