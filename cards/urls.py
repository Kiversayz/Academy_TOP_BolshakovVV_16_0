from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.card_templates_list, name='templates_list'),  # Теперь работает для /cards/
]