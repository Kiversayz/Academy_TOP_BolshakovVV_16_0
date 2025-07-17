# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.db.models import F

class User(AbstractUser):
    # Убираем username, используем email как идентификатор
    username = None
    email = models.EmailField(
        unique=True,
        verbose_name='Email',
        help_text='Будет использоваться для входа в систему'
    )

    # Контактные данные
    phone = models.CharField(
        max_length=35,
        verbose_name='Телефон',
        blank=True,
        null=True,
        help_text='Формат: +79991234567'
    )
    telegram = models.CharField(
        max_length=150,
        verbose_name='Telegram',
        blank=True,
        null=True,
        help_text='Без @, например: username'
    )

    # Личные данные
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя',
        blank=True,
        null=True
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия',
        blank=True,
        null=True
    )
    third_name = models.CharField(
        max_length=100,
        verbose_name='Отчество',
        blank=True,
        null=True
    )

    # Визуальные настройки
    avatar = models.ImageField(
        upload_to='users/avatars/%Y/%m/',
        verbose_name='Аватар',
        blank=True,
        null=True,
        help_text='Рекомендуемый размер: 200x200 px'
    )

    # Статусы
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активный',
        help_text='Отключенные пользователи не могут войти в систему'
    )

    # Роли пользователей
    class Role(models.TextChoices):
        CREATOR = 'CREATOR', 'Креатор'
        EDITOR = 'EDITOR', 'Редактор'
        MODERATOR = 'MODERATOR', 'Модератор'
        ADMIN = 'ADMIN', 'Администратор'
        USER = 'USER', 'Пользователь'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name='Роль',
        help_text='Определяет права пользователя в системе'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Убрано 'username'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
        permissions = [
        ("can_invite_users", "Может приглашать новых пользователей"),
        ("can_manage_users", "Может управлять пользователями"),
        ]

    def __str__(self):
        return f'{self.email} ({self.role})'

    def clean(self):
        """Валидация данных перед сохранением"""
        super().clean()

        # Проверка email
        if self.email:
            self.email = self.email.lower().strip()

        # Проверка Telegram
        if self.telegram and self.telegram.startswith('@'):
            self.telegram = self.telegram[1:]

        # Проверка телефона
        if self.phone and not self.phone.startswith('+'):
            raise ValidationError("Телефон должен начинаться с '+', например: +79991234567")

    def save(self, *args, **kwargs):
        """Автоматическое назначение ролей и обработка перед сохранением"""
        # Суперпользователь всегда администратор
        if self.is_superuser:
            self.role = self.Role.ADMIN
        # Статья администратора
        elif self.is_staff and self.role not in (self.Role.ADMIN, self.Role.MODERATOR):
            self.role = self.Role.MODERATOR
        # Новые пользователи по умолчанию - пользователи
        elif not self.pk:
            self.role = self.Role.USER

        super().save(*args, **kwargs)

    @property
    def is_guest(self):
        """Проверка, является ли пользователь гостем (анонимным)"""
        return not self.is_authenticated

    @property
    def is_creator(self):
        """Проверка, является ли пользователь создателем или администратором"""
        return self.role in (self.Role.CREATOR, self.Role.ADMIN)

    @property
    def can_moderate(self):
        """Проверка, может ли пользователь модерировать контент"""
        return self.role in (self.Role.MODERATOR, self.Role.ADMIN)

    @classmethod
    def get_default_role(cls):
        """Возвращает роль по умолчанию"""
        return cls.Role.USER