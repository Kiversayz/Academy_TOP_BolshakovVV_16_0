import json
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CardTemplate
from django.core.validators import MinLengthValidator


class CardTemplateForm(forms.ModelForm):
    class Meta:
        model = CardTemplate
        fields = ['name', 'description', 'fields', 'is_public', 'is_favorite']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Введите название шаблона')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': _('Краткое описание шаблона...'),
                'rows': 3,
            }),
            'fields': forms.Textarea(attrs={
                'class': 'form-control font-monospace',
                'placeholder': _('JSON-структура полей'),
                'rows': 8,
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_favorite': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'fields': _('JSON-структура'),
            'is_public': _('Публичный доступ'),
        }
        help_texts = {
            'fields': _('Пример: {"field1": {"type": "text", "label": "Название"}}')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        
        # Добавляем валидацию минимальной длины для имени
        self.fields['name'].validators = [
            MinLengthValidator(
                3,
                message=_('Название должно содержать минимум 3 символа')
            )
        ]

    def clean_fields(self):
        """Основная валидация JSON-поля."""
        fields_data = self.cleaned_data.get('fields', {})
        
        # Если данные уже в dict (например, из админки)
        if isinstance(fields_data, dict):
            return fields_data

        try:
            parsed_data = json.loads(fields_data)
            if not isinstance(parsed_data, dict):
                raise ValidationError(_("Требуется JSON-объект (словарь)"))
            return parsed_data
        except json.JSONDecodeError as e:
            raise ValidationError(
                _("Ошибка в JSON: %(error)s") % {'error': str(e)}
            )

    def clean(self):
        """Дополнительная валидация всей формы."""
        cleaned_data = super().clean()
        
        # Автоматически вызываем clean_fields()
        if 'fields' in self.errors:
            return cleaned_data
            
        # Дополнительные проверки структуры JSON
        fields_data = cleaned_data.get('fields', {})
        if not fields_data:
            raise ValidationError({'fields': _("Структура полей не может быть пустой")})
            
        # Проверка минимального количества полей
        if len(fields_data) < 1:
            raise ValidationError(
                {'fields': _("Должно быть хотя бы одно поле")}
            )
            
        return cleaned_data