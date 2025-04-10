# Generated by Django 5.0.13 on 2025-04-01 18:59

import cards.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CardTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Максимальная длина — 100 символов. Пример: 'Карточки для викторины'", max_length=100, verbose_name='Название шаблона')),
                ('fields', models.JSONField(help_text='\n            JSON-структура с описанием полей. Пример:\n            {\n                "image": {\n                    "type": "image", \n                    "label": "Изображение",\n                    "max_size": 1024  // в килобайтах (опционально)\n                },\n                "question": {\n                    "type": "text", \n                    "label": "Вопрос",\n                    "max_length": 200\n                }\n            }\n        ', validators=[cards.models.validate_fields_structure], verbose_name='Поля шаблона')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Автоматически устанавливается при создании', verbose_name='Дата создания')),
                ('creator', models.ForeignKey(help_text='Пользователь, создавший этот шаблон', on_delete=django.db.models.deletion.CASCADE, related_name='templates', to=settings.AUTH_USER_MODEL, verbose_name='Создатель')),
            ],
            options={
                'verbose_name': 'Шаблон карточки',
                'verbose_name_plural': 'Шаблоны карточек',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['name'], name='cards_cardt_name_6a52e5_idx')],
            },
        ),
    ]
