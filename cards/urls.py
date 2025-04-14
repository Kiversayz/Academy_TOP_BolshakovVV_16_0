from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.card_templates_list, name='templates_list'),
    path('templates/', views.card_templates_list, name='templates_list'),  # /cards/templates/
    path('create/', views.create_template, name='create_template'),
]