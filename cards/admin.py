from django.contrib import admin
from .models import CardTemplate

@admin.register(CardTemplate)
class CardTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'created_at')
