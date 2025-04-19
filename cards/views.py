from typing import Any, Dict
from django.db.models import Count, Q, QuerySet
from django.views.generic import (
    ListView, DetailView, 
    CreateView, UpdateView, 
    DeleteView
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin, 
    UserPassesTestMixin
)
from django.urls import reverse_lazy
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from .models import CardTemplate, CardInstance
from .forms import CardTemplateForm
from .services import TemplatePermissionService
from .constants import UserRoles


class TemplateListView(ListView):
    """
    Отображает список шаблонов карточек с учетом прав доступа.
    Реализует пагинацию и аннотацию количества карточек.
    """
    model = CardTemplate
    template_name = 'cards/template_list.html'
    context_object_name = 'templates'
    paginate_by = 10
    ordering = ['-created_at']

    def get_queryset(self) -> QuerySet:
        """Возвращает QuerySet с учетом роли пользователя."""
        queryset = super().get_queryset().annotate(
            cards_count=Count('instances')
        )

        if not self.request.user.is_authenticated:
            return queryset.filter(is_public=True)

        if self.request.user.role == UserRoles.ADMIN:
            return queryset

        if self.request.user.role == UserRoles.MODERATOR:
            return queryset.filter(Q(is_public=True) | Q(creator=self.request.user))

        if self.request.user.role == UserRoles.CREATOR:
            return queryset.filter(
                Q(is_public=True) | 
                Q(creator=self.request.user) |
                Q(editors=self.request.user)
            )

        return queryset.filter(is_public=True)


class TemplateDetailView(DetailView):
    """Детальное представление шаблона с проверкой прав доступа."""
    model = CardTemplate
    template_name = 'cards/template_detail.html'
    context_object_name = 'template'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """Проверяет доступ к шаблону перед отображением."""
        template = self.get_object()
        if not TemplatePermissionService.can_view_template(request.user, template):
            raise PermissionDenied("У вас нет прав для просмотра этого шаблона")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Добавляет флаг возможности редактирования в контекст."""
        context = super().get_context_data(**kwargs)
        context['can_edit'] = TemplatePermissionService.can_edit_template(
            self.request.user, self.object
        )
        return context


class TemplateCreateView(LoginRequiredMixin, CreateView):
    """Создание нового шаблона карточек."""
    model = CardTemplate
    form_class = CardTemplateForm
    template_name = 'cards/template_form.html'
    success_url = reverse_lazy('cards:templates_list')

    def form_valid(self, form: CardTemplateForm) -> HttpResponseRedirect:
        """Устанавливает создателя шаблона перед сохранением."""
        form.instance.creator = self.request.user
        return super().form_valid(form)


class TemplateUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование существующего шаблона."""
    model = CardTemplate
    form_class = CardTemplateForm
    template_name = 'cards/template_form.html'

    def test_func(self) -> bool:
        """Проверяет права на редактирование шаблона."""
        return TemplatePermissionService.can_edit_template(
            self.request.user, self.get_object()
        )

    def get_success_url(self) -> str:
        """Перенаправляет на страницу шаблона после редактирования."""
        return reverse_lazy('cards:template_detail', kwargs={'pk': self.object.pk})


class TemplateDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Мягкое удаление шаблона (is_active=False)."""
    model = CardTemplate
    template_name = 'cards/template_confirm_delete.html'
    success_url = reverse_lazy('cards:templates_list')

    def test_func(self) -> bool:
        """Проверяет права на удаление шаблона."""
        return TemplatePermissionService.can_delete_template(
            self.request.user, self.get_object()
        )

    def delete(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        """Выполняет мягкое удаление вместо полного."""
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class CardInstanceCreateView(LoginRequiredMixin, CreateView):
    """Создание экземпляра карточки на основе шаблона."""
    model = CardInstance
    fields = ['data']
    template_name = 'cards/cardinstance_form.html'

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> Any:
        """Получает шаблон и проверяет права доступа."""
        self.template = get_object_or_404(CardTemplate, pk=kwargs['template_pk'])
        if not TemplatePermissionService.can_add_card_instance(request.user, self.template):
            raise PermissionDenied("У вас нет прав для создания карточек в этом шаблоне")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: CardTemplateForm) -> HttpResponseRedirect:
        """Устанавливает шаблон и создателя перед сохранением."""
        form.instance.template = self.template
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Перенаправляет на страницу шаблона после создания."""
        return reverse_lazy('cards:template_detail', kwargs={'pk': self.template.pk})

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Добавляет шаблон в контекст."""
        context = super().get_context_data(**kwargs)
        context['template'] = self.template
        return context