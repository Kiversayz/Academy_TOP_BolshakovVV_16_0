from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator
from users.models import User
from typing import Dict, Any
from django.urls import reverse

class FieldType(models.TextChoices):
    """Типы полей для шаблонов карточек."""
    TEXT = 'text', _('Текст')
    TEXTAREA = 'textarea', _('Многострочный текст')
    IMAGE = 'image', _('Изображение')
    NUMBER = 'number', _('Число')
    SELECT = 'select', _('Выпадающий список')

def validate_fields_structure(value: Dict[str, Any]) -> None:
    """
    Валидатор структуры JSON-поля fields.
    
    Args:
        value: Словарь с конфигурацией полей
        
    Raises:
        ValidationError: Если структура не соответствует требованиям
    
    Example:
        {
            "term": {
                "type": "text", 
                "label": "Термин",
                "required": True
            },
            "image": {
                "type": "image",
                "label": "Изображение",
                "max_size": 2048
            }
        }
    """
    if not isinstance(value, dict):
        raise ValidationError(_("Основная структура должна быть словарем."))

    for field_name, config in value.items():
        if not isinstance(config, dict):
            raise ValidationError(
                _("Поле '%(field)s' должно быть словарем.") % {'field': field_name}
            )
        
        # Проверка обязательных полей
        required_fields = {'type', 'label'}
        missing_fields = required_fields - config.keys()
        if missing_fields:
            raise ValidationError(
                _("Поле '%(field)s' не содержит обязательные ключи: %(missing)s") % {
                    'field': field_name,
                    'missing': ', '.join(missing_fields)
                }
            )
        
        # Проверка типа поля
        field_type = config.get('type')
        if field_type not in FieldType.values:
            raise ValidationError(
                _("Недопустимый тип '%(type)s' для поля '%(field)s'. Допустимые типы: %(allowed)s") % {
                    'type': field_type,
                    'field': field_name,
                    'allowed': ', '.join(FieldType.values)
                }
            )
        
        # Дополнительные проверки для специфичных типов
        if field_type == FieldType.SELECT and 'options' not in config:
            raise ValidationError(
                _("Поле '%(field)s' типа 'select' требует указания options") % {'field': field_name}
            )


class CardTemplate(models.Model):
    """
    Шаблон для создания карточек с настраиваемой структурой полей.
    
    Attributes:
        name: Название шаблона (макс. 100 символов)
        creator: Пользователь, создавший шаблон
        fields: Конфигурация полей в JSON-формате
        preview_image: Превью изображение шаблона (бэклог)
        is_public: Флаг публичного доступа
        description: Описание шаблона
        is_favorite: Флаг избранного
        editors: Пользователи с правами редактирования
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("Название шаблона"),
        help_text=_("Максимальная длина — 100 символов"),
        validators=[MinLengthValidator(3)]
    )
    
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Создатель"),
        related_name="templates",
        help_text=_("Пользователь, создавший этот шаблон")
    )
    
    fields = models.JSONField(
        verbose_name=_("Поля шаблона"),
        validators=[validate_fields_structure],
        help_text=_("JSON-структура с описанием полей карточки")
    )
    
    #preview_image = models.ImageField(
    #    upload_to='card_templates/previews/%Y/%m/%d/',
    #    verbose_name=_("Превью шаблона"),
    #    blank=True,
    #    null=True,
    #    help_text=_("Изображение для предпросмотра шаблона")
    #)
    
    is_public = models.BooleanField(
        default=False,
        verbose_name=_("Публичный доступ"),
        help_text=_("Доступен ли шаблон всем пользователям")
    )
    
    description = models.TextField(
        verbose_name=_("Описание"),
        blank=True,
        help_text=_("Краткое описание шаблона")
    )
    
    is_favorite = models.BooleanField(
        default=False,
        verbose_name=_("Избранное"),
        help_text=_("Пометить шаблон как избранное")
    )
    
    editors = models.ManyToManyField(
        User,
        related_name="editable_templates",
        blank=True,
        verbose_name=_("Редакторы"),
        help_text=_("Пользователи, имеющие право редактировать шаблон")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )

    class Meta:
        verbose_name = _("Шаблон карточки")
        verbose_name_plural = _("Шаблоны карточек")
        permissions = [
            ("can_export_pdf", "Можно экспортировать в PDF"),
            ("can_export_json", "Можно экспортировать в JSON"),
            ("can_change_template", "Можно изменить шаблон"),
            ("can_delete_template", "Можно удалить шаблон"),
            ("view_public_templates", "Можно просматривать публичные шаблоны"),
        ]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_public", "is_favorite"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'creator'],
                name='unique_template_name_per_creator'
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.id})"
    
    def clean(self) -> None:
        """Дополнительная валидация модели перед сохранением."""
        super().clean()
        validate_fields_structure(self.fields)
        if len(self.name.strip()) < 3:
            raise ValidationError(
                _("Название шаблона должно содержать минимум 3 символа")
            )
    
    def save(self, *args, **kwargs):
        if self.pk:
            # Инкремент версии при изменениях
            original = CardTemplate.objects.get(pk=self.pk)
            if original.fields != self.fields:
                self.version += 1
        super().save(*args, **kwargs)


class CardInstance(models.Model):
    """
    Конкретный экземпляр карточки, созданный по шаблону.
    
    Attributes:
        template: Ссылка на шаблон
        data: Данные карточки в JSON-формате
        created_by: Пользователь, создавший карточку
    """
    
    template = models.ForeignKey(
        CardTemplate,
        on_delete=models.CASCADE,
        related_name="instances",
        verbose_name=_("Шаблон")
    )
    
    data = models.JSONField(
        verbose_name=_("Данные карточки"),
        help_text=_("Заполненные данные согласно структуре шаблона")
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Создатель"),
        related_name="created_cards"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Дата создания")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Дата обновления")
    )
    
    meta_data = models.JSONField(
        verbose_name=_("Метаданные"),
        blank=True,
        null=True,
        default=dict,
        help_text=_("Дополнительные данные, например, источник, версия шаблона и др.")
    )

    class Meta:
        verbose_name = _("Экземпляр карточки")
        verbose_name_plural = _("Экземпляры карточек")
        permissions = [
        ("can_export_pdf", "Можно экспортировать в PDF"),
        ("can_export_json", "Можно экспортировать в JSON"),
        ("moderate_content", "Может модерировать контент"),
        ("view_public_templates", "Может просматривать публичные шаблоны"),
        ]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["template", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Карточка {self.id} (Шаблон: {self.template_id})"
        
    def clean(self) -> None:
        """Валидация данных карточки согласно шаблону."""
        super().clean()
        if not isinstance(self.data, dict):
            raise ValidationError(
                _("Данные карточки должны быть в формате JSON-объекта")
            )

    def get_absolute_url(self):
        return reverse('cards:instance_detail', kwargs={'pk': self.pk})