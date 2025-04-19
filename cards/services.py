from .models import CardTemplate
from .constants import UserRoles

class TemplatePermissionService:
    """Сервис для централизованной проверки прав доступа."""

    @staticmethod
    def can_view_template(user, template) -> bool:
        """Может ли пользователь просматривать шаблон."""
        if template.is_public:
            return True
        if not user.is_authenticated:
            return False
        return (user.role in [UserRoles.ADMIN, UserRoles.MODERATOR] or 
                template.creator == user or 
                user in template.editors.all())

    @staticmethod
    def can_edit_template(user, template) -> bool:
        """Может ли пользователь редактировать шаблон."""
        if not user.is_authenticated:
            return False
        return (user.role in [UserRoles.ADMIN, UserRoles.MODERATOR] or 
                template.creator == user or 
                user in template.editors.all())

    @staticmethod
    def can_delete_template(user, template) -> bool:
        """Может ли пользователь удалять шаблон."""
        return user.is_authenticated and (
            user.role == UserRoles.ADMIN or 
            template.creator == user
        )

    @staticmethod
    def can_add_card_instance(user, template) -> bool:
        """Может ли пользователь добавлять карточки к шаблону."""
        return TemplatePermissionService.can_edit_template(user, template)