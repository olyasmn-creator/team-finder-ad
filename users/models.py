from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import io
import random


class CustomUserManager(BaseUserManager):
    """
    Кастомный менеджер для модели User
    Переопределяем методы создания пользователя, чтобы использовать email вместо username
    """
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Поле Email обязательно для заполнения')
        
        # Нормализуем email (приводим к нижнему регистру)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Для суперпользователя обязательно ставим флаги is_staff и is_superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Кастомная модель пользователя для TeamFinder
    Вход осуществляется по email
    """
    # Отключаем стандартное поле username, так как мы используем email
    username = None
    
    # Обязательные поля
    email = models.EmailField('email address', unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    
    # Аватар генерируется автоматически, но поле должно быть заполнено
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    
    # Телефон: макс. 12 символов (формат +79991234567), должен быть уникальным
    phone = models.CharField(
        max_length=12,
        unique=True,
        blank=True,
        null=True,
        default='',
    ) 
    
    # Дополнительные поля
    github_url = models.URLField(blank=True, null=True)
    about = models.TextField(max_length=256, blank=True)
    
    # Статусы пользователя
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # === Навыки пользователей ===
    # Связь Many-to-Many с моделью Skill
    skills = models.ManyToManyField('Skill', blank=True, related_name='users')

    # Указываем, что поле для входа — это email
    USERNAME_FIELD = 'email'
    # Поля, которые обязательно спрашивать при создании пользователя через createsuperuser
    REQUIRED_FIELDS = ['name', 'surname']

    # Подключаем наш кастомный менеджер
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.surname} {self.name}"

    def save(self, *args, **kwargs):
        """
        Переопределяем метод save для автоматической генерации аватара,
        если пользователь новый и у него нет загруженной картинки.
        """
        # Генерируем аватар только при создании нового пользователя (если аватар пуст)
        if not self.pk and not self.avatar and self.name:
            self.avatar = self._generate_default_avatar()
        
        # Нормализация телефона: приводим формат 8.. к +7..
        if self.phone:
            # Убираем лишние символы (пробелы, тире, скобки)
            clean_phone = ''.join(filter(str.isdigit, self.phone))
            if clean_phone.startswith('8') and len(clean_phone) == 11:
                self.phone = '+7' + clean_phone[1:]
            elif clean_phone.startswith('7') and len(clean_phone) == 11:
                self.phone = '+' + clean_phone
            else:
                self.phone = clean_phone # сохраняем как есть, если формат странный

        super().save(*args, **kwargs)

    def _generate_default_avatar(self, size=(200, 200)):
        """
        Создает изображение-заглушку: первая буква имени на цветном фоне.
        Возвращает объект ContentFile для сохранения в ImageField.
        """
        # Палитра приятных цветов (RGB)
        colors = [
            (52, 152, 219),   # Голубой
            (155, 89, 182),   # Фиолетовый
            (46, 204, 113),   # Зеленый
            (241, 196, 15),   # Желтый
            (230, 126, 34),   # Оранжевый
            (231, 76, 60),    # Красный
        ]
        
        # Выбираем случайный цвет
        bg_color = random.choice(colors)
        
        # Создаем изображение
        image = Image.new('RGB', size, bg_color)
        draw = ImageDraw.Draw(image)
        
        # Берем первую букву имени
        initial = self.name[0].upper()
        
        # Пытаемся загрузить шрифт, если нет — используем стандартный
        try:
            # Путь к шрифту может отличаться в зависимости от ОС
            font = ImageFont.truetype("arial.ttf", 100)
        except IOError:
            font = ImageFont.load_default()

        # Вычисляем размер текста для центрирования 
        try:
            bbox = draw.textbbox((0, 0), initial, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # Fallback для очень старых версий
            text_width, text_height = draw.textsize(initial, font=font)

        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # Рисуем белый текст
        draw.text((x, y), initial, fill='white', font=font)
        
        # Сохраняем в буфер памяти
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Возвращаем файл с уникальным именем
        filename = f"avatar_default_{self.email.split('@')[0]}.png"
        return ContentFile(buffer.getvalue(), name=filename)


class Skill(models.Model):
    """
    Модель навыка.
    Используется для тегов в профилях пользователей.
    """
    name = models.CharField(max_length=124, unique=True)

    class Meta:
        ordering = ['name']  # Сортируем навыки по алфавиту по умолчанию
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name
