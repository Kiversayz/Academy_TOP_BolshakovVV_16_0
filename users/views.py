from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView
from cards.models import CardTemplate
from django.db.models import Count
from .models import User
from django.http import HttpRequest
from django.contrib.auth import get_user_model

User = get_user_model()  # Используем get_user_model() для получения модели пользователя

class RoleRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки прав на основе роли пользователя."""
    roles_required = []
    permission_required = None

    def test_func(self) -> bool:
        request: HttpRequest = self.request
        user = request.user
        if not user.is_authenticated:
            return False

        user_role = getattr(user, 'role', None)
        if not user_role or user_role not in self.roles_required:
            return False

        if self.permission_required:
            return user.has_perm(self.permission_required)
        
        return True


class HomeView(RoleRequiredMixin, TemplateView):
    """
    Главная страница с контекстом для отображения шаблонов и информации о пользователе.
    """
    template_name = 'home.html'
    roles_required = [User.Role.CREATOR, User.Role.ADMIN, User.Role.EDITOR, User.Role.MODERATOR, User.Role.USER]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            user_role = getattr(user, 'role', None)
            if user_role in [User.Role.CREATOR, User.Role.ADMIN]:
                context['user_templates'] = CardTemplate.objects.filter(
                    creator=user
                ).order_by('-created_at')[:5]

        context['popular_templates'] = CardTemplate.objects.filter(
            is_public=True
        ).annotate(
            num_cards=Count('instances')
        ).order_by('-num_cards')[:5]

        context['user_role'] = user.role if user.is_authenticated else None

        return context