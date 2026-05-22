import io
import random

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from .constants import (
    AVATAR_DEFAULT_SIZE,
    AVATAR_FONT_SIZE,
    AVATAR_TEXT_COLOR,
    NAME_MAX_LENGTH,
    SURNAME_MAX_LENGTH,
    ABOUT_MAX_LENGTH,
    PHONE_MAX_LENGTH,
    AVATAR_COLORS,
)


class UserManager(BaseUserManager):
    """
    Менеджер для модели User.
    Переопределяем методы создания пользователя, чтобы использовать email вместо username.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Поле Email обязательно для заполнения')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя для TeamFinder.
    Вход осуществляется по email.
    """
    username = None
    
    email = models.EmailField('email address', unique=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    surname = models.CharField(max_length=SURNAME_MAX_LENGTH)
    
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
        default='',
    ) 
    
    github_url = models.URLField(blank=True, null=True)
    about = models.TextField(max_length=ABOUT_MAX_LENGTH, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    skills = models.ManyToManyField('Skill', blank=True, related_name='users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    def __str__(self):
        return f"{self.surname} {self.name}"

    def save(self, *args, **kwargs):
        """
        Переопределяем метод save для автоматической генерации аватара,
        если пользователь новый и у него нет загруженной картинки.
        """
        if not self.pk and not self.avatar and self.name:
            self.avatar = self._generate_default_avatar()
        
        if self.phone:
            clean_phone = ''.join(filter(str.isdigit, self.phone))
            if clean_phone.startswith('8') and len(clean_phone) == 11:
                self.phone = '+7' + clean_phone[1:]
            elif clean_phone.startswith('7') and len(clean_phone) == 11:
                self.phone = '+' + clean_phone
            else:
                self.phone = clean_phone

        super().save(*args, **kwargs)

    def _generate_default_avatar(self, size=AVATAR_DEFAULT_SIZE):
        """
        Создает изображение-заглушку: первая буква имени на цветном фоне.
        Возвращает объект ContentFile для сохранения в ImageField.
        """
        bg_color = random.choice(AVATAR_COLORS)
        
        image = Image.new('RGB', size, bg_color)
        draw = ImageDraw.Draw(image)
        
        initial = self.name[0].upper()
        
        try:
            font = ImageFont.truetype("arial.ttf", AVATAR_FONT_SIZE)
        except IOError:
            font = ImageFont.load_default()

        try:
            bbox = draw.textbbox((0, 0), initial, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(initial, font=font)

        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), initial, fill=AVATAR_TEXT_COLOR, font=font)
        
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        
        filename = f"avatar_default_{self.email.split('@')[0]}.png"
        return ContentFile(buffer.getvalue(), name=filename)


class Skill(models.Model):
    """
    Модель навыка.
    Используется для тегов в профилях пользователей.
    """
    name = models.CharField(max_length=124, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name
    
