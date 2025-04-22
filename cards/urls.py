from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    path('', views.card_template_list, name='template_list'),
    path('create/', views.create_template, name='create_template'),
    path('<int:pk>/', views.template_detail, name='template_detail'),
    path('<int:pk>/edit/', views.template_update, name='template_update'),
    path('<int:pk>/delete/', views.template_delete, name='template_delete'),
    path('<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('<int:pk>/publish/', views.publish_template, name='publish_template'),
    path('<int:pk>/unpublish/', views.unpublish_template, name='unpublish_template'),
    path('<int:template_id>/create-card/', views.create_card_instance, name='create_card_instance'),
]
