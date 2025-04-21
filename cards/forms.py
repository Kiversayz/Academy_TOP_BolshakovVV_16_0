import json
from django import forms
from django.core.exceptions import ValidationError
from .models import CardTemplate

class CardTemplateForm(forms.ModelForm):
    class Meta:
        model = CardTemplate
        fields = ['name', 'description', 'fields', 'preview_image', 'is_public', 'is_favorite']
        widgets = {
            'description': forms.Textarea(attrs={
                'placeholder': 'Краткое описание шаблона…',
                'rows': 3,
            }),
            'fields': forms.Textarea(attrs={
                'placeholder': '{"term": {"type": "text", "label": "Термин"}, "definition": {"type": "textarea", "label": "Определение"}}',
                'rows': 6,
                'class': 'form-control font-monospace',
            }),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_favorite': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preview_image'].required = False
        self.fields['fields'].required = True
        self.fields['description'].required = False

    def clean_fields(self):
        # Базовый метод, не нужен — Django вызывает его сам.
        return self.cleaned_data.get('fields', {})

    def clean_fields_json(self):
        """
        Валидирует поле `fields`, если оно введено как строка.
        """
        data = self.cleaned_data.get('fields')

        # Если уже словарь — ок (например, из админки)
        if isinstance(data, dict):
            return data

        try:
            parsed = json.loads(data)
            if not isinstance(parsed, dict):
                raise ValidationError("Поле должно быть JSON-объектом.")
            return parsed
        except json.JSONDecodeError:
            raise ValidationError("Ошибка разбора JSON: некорректный формат.")

    def clean(self):
        """
        Переопределяет глобальную валидацию формы.
        """
        cleaned_data = super().clean()
        cleaned_data['fields'] = self.clean_fields_json()
        return cleaned_data


