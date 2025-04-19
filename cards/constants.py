from django.db import models

class UserRoles(models.TextChoices):
    """Роли пользователей."""
    GUEST = 'GUEST', 'Гость'
    USER = 'USER', 'Пользователь'
    CREATOR = 'CREATOR', 'Создатель'
    EDITOR = 'EDITOR', 'Редактор'
    MODERATOR = 'MODERATOR', 'Модератор'
    ADMIN = 'ADMIN', 'Администратор'