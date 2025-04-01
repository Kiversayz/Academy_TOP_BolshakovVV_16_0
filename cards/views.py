# cards/views.py
from django.shortcuts import render
from .models import CardTemplate

def card_templates_list(request):
    templates = CardTemplate.objects.all()
    return render(request, 'cards/templates_list.html', {'templates': templates})