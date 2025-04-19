from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class User(AbstractUser):
    # Убираем username, используем email как идентификатор
    username = None
    email = models.EmailField(
        unique=True,
        verbose_name=_('Email'),
        help_text=_('Будет использоваться для входа в систему')
    )
    
    # Контактные данные
    phone = models.CharField(
        max_length=35,
        verbose_name=_('Телефон'),
        blank=True,
        null=True,
        help_text=_('Формат: +79991234567')
    )
    telegram = models.CharField(
        max_length=150,
        verbose_name=_('Telegram'),
        blank=True,
        null=True,
        help_text=_('Без @, например: username')
    )
    
    # Визуальные настройки
    avatar = models.ImageField(
        upload_to='users/avatars/%Y/%m/',
        verbose_name=_('Аватар'),
        blank=True,
        null=True,
        help_text=_('Рекомендуемый размер: 200x200 px')
    )
    
    # Статусы
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активный'),
        help_text=_('Отключенные пользователи не могут войти в систему')
    )
    
    # Роли пользователей
    class Role(models.TextChoices):
        GUEST = 'GUEST', _('Гость')
        USER = 'USER', _('Пользователь')
        CREATOR = 'CREATOR', _('Создатель')
        EDITOR = 'EDITOR', _('Редактор')
        MODERATOR = 'MODERATOR', _('Модератор')
        ADMIN = 'ADMIN', _('Администратор')
    
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
        verbose_name=_('Роль'),
        help_text=_('Определяет права пользователя в системе')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['-date_joined']
        permissions = [
            ("can_export_pdf", _("Может экспортировать в PDF")),
            ("manage_private_templates", _("Доступ к приватным шаблонам")),
            ("moderate_content", _("Может модерировать контент")),
            ("invite_editors", _("Может приглашать редакторов")),
        ]

    def __str__(self):
        return f'{self.email} ({self.get_role_display()})'

    def clean(self):
        """Валидация данных перед сохранением"""
        super().clean()
        
        # Проверка email
        if self.email:
            self.email = self.email.lower().strip()
            
        # Проверка Telegram
        if self.telegram and self.telegram.startswith('@'):
            self.telegram = self.telegram[1:]

    def save(self, *args, **kwargs):
        """Автоматическое назначение ролей и обработка перед сохранением"""
        self.full_clean()  # Вызов валидации
        
        # Автоназначение ролей для администраторов
        if self.is_superuser:
            self.role = self.Role.ADMIN
        elif self.is_staff and self.role not in (self.Role.ADMIN, self.Role.MODERATOR):
            self.role = self.Role.MODERATOR
            
        # Для новых пользователей
        if not self.pk and self.role == self.Role.GUEST:
            self.role = self.Role.USER
            
        super().save(*args, **kwargs)

    @property
    def is_guest(self):
        return self.role == self.Role.GUEST or not self.is_authenticated

    @property
    def is_creator(self):
        return self.role in (self.Role.CREATOR, self.Role.ADMIN)

    @property
    def can_moderate(self):
        return self.role in (self.Role.MODERATOR, self.Role.ADMIN)

    @classmethod
    def get_default_role(cls):
        return cls.Role.USER