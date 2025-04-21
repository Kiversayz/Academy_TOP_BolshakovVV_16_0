from django.contrib import admin
from .models import CardTemplate, CardInstance

@admin.register(CardTemplate)
class CardTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'is_public')
    search_fields = ('name',)

admin.site.register(CardInstance)
