from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    path('templates/', views.TemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.TemplateCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/', views.TemplateDetailView.as_view(), name='template_detail'),
    path('templates/<int:pk>/edit/', views.TemplateUpdateView.as_view(), name='template_update'),
    path('templates/<int:pk>/delete/', views.TemplateDeleteView.as_view(), name='template_delete'),
]