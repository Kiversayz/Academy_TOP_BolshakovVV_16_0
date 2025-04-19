from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView
from cards.models import CardTemplate
from django.db.models import Count


class RoleRequiredMixin(UserPassesTestMixin):
    roles_required = []
    
    def test_func(self):
        return self.request.user.role in self.roles_required

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Добавляем данные для разных ролей
        if user.is_authenticated and hasattr(user, 'role'):
            if user.role in ['CREATOR', 'ADMIN']:
                context['user_templates'] = CardTemplate.objects.filter(creator=user)[:5]
        
        # Популярные шаблоны (используем аннотацию для лайков)
        context['popular_templates'] = CardTemplate.objects.filter(
            is_public=True
        ).annotate(
            num_cards=Count('cards')  # Используем related_name 'cards' из CardInstance
        ).order_by('-num_cards')[:5]
        
        # Добавляем user_role в контекст
        context['user_role'] = user.role if user.is_authenticated else 'GUEST'
        
        return context
