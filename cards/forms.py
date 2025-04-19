from django import forms
from django.core.exceptions import ValidationError
from .models import CardTemplate
import json

class CardTemplateForm(forms.ModelForm):
    class Meta:
        model = CardTemplate
        fields = ['name', 'description', 'fields', 'preview_image', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'fields': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preview_image'].required = False

    def clean_fields(self):
        data = self.cleaned_data.get('fields', '{}')

        # Проверка на допустимость JSON
        try:
            parsed_data = json.loads(data)
            if not isinstance(parsed_data, dict):
                raise ValidationError("Данные должны быть в формате JSON-объекта.")
            return parsed_data
        except json.JSONDecodeError:
            raise ValidationError("Некорректный JSON-формат.")

