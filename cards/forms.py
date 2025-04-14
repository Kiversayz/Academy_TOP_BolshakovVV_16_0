import json
from django import forms
from django.core.exceptions import ValidationError
from .models import CardTemplate

class CardTemplateForm(forms.ModelForm):
    class Meta:
        model = CardTemplate
        fields = ['name', 'fields', 'preview_image']
        widgets = {
            'fields': forms.Textarea(attrs={
                'placeholder': '{"field1": {"type": "text", "label": "..."}, ...}',
                'rows': 5 
            })
        }

    def clean_fields(self):
        data = self.cleaned_data.get('fields', {})
        
        # Если данные уже словарь (например, из админки)
        if isinstance(data, dict):
            return data
            
        try:
            parsed_data = json.loads(data)
            if not isinstance(parsed_data, dict):
                raise ValidationError("Данные должны быть JSON-объектом.")
            return parsed_data
        except json.JSONDecodeError:
            raise ValidationError("Некорректный JSON-формат.")
