from django.db import models
from users.models import User


class Project(models.Model):
    """
    Модель проекта для платформы TeamFinder
    Представляет pet-проект, который создаёт пользователь для поиска команды
    """
    
    # Варианты статуса проекта (длина до 6 символов)
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_CLOSED, 'Closed'),
    ]
    
    # === Основные поля проекта ===
    
    # Название проекта (до 200 символов)
    name = models.CharField(max_length=200)
    
    # Подробное описание (необязательное)
    description = models.TextField(blank=True)
    
    # Автор проекта — внешний ключ на пользователя
    # related_name позволяет обращаться: user.owned_projects
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    
    # Дата создания — заполняется автоматически при первом сохранении
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Ссылка на репозиторий GitHub (необязательная)
    github_url = models.URLField(blank=True)
    
    # Статус проекта: открыт или закрыт
    status = models.CharField(
        max_length=6,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN
    )
    
    # Участники проекта — связь многие-ко-многим с пользователями
    # related_name позволяет обращаться: user.participated_projects
    participants = models.ManyToManyField(
        User,
        blank=True,
        related_name='participated_projects'
    )
    
    class Meta:
        """
        Мета-настройки модели
        """
        # Сортировка по умолчанию: новые проекты сверху
        ordering = ['-created_at']
        # Человеко-читаемые названия для админки
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
    
    def __str__(self):
        """
        Строковое представление объекта (отображается в админке и shell)
        """
        return self.name
    
    # === Дополнительные методы (опционально, для удобства) ===
    
    def is_owner(self, user):
        """
        Проверка: является ли переданный пользователь владельцем проекта
        """
        return self.owner == user
    
    def get_participants_count(self):
        """
        Возвращает количество участников проекта
        """
        return self.participants.count()
    
    def toggle_participant(self, user):
        """
        Переключает участие пользователя: добавляет, если нет,
        или удаляет, если пользователь уже в участниках
        """
        if self.participants.filter(pk=user.pk).exists():
            self.participants.remove(user)
            return False  # Пользователь был удалён
        else:
            self.participants.add(user)
            return True  # Пользователь был добавлен
