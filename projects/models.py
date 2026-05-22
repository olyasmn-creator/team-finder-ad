from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


NAME_MAX_LENGTH = 200
STATUS_MAX_LENGTH = 6


class Project(models.Model):
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_CLOSED, 'Closed'),
    ]
    
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True)
    status = models.CharField(
        max_length=STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN
    )
    participants = models.ManyToManyField(
        User,
        blank=True,
        related_name='participated_projects'
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
    
    def __str__(self):
        return self.name
    
    def is_owner(self, user):
        return self.owner == user
    
    def get_participants_count(self):
        return self.participants.count()
    
    def toggle_participant(self, user):
        if self.participants.filter(pk=user.pk).exists():
            self.participants.remove(user)
            return False
        self.participants.add(user)
        return True
    
