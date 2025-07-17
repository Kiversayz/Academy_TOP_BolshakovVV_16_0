# users/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from cards.models import CardTemplate, CardInstance
from users.models import User

@receiver(post_save, sender=User)
def assign_permissions_on_save(sender, instance, created, **kwargs):
    """
    Присваивает разрешения пользователю на основе его роли при сохранении.
    """
    if instance.is_superuser or not instance.is_authenticated:
        return

    # Словарь разрешений для каждой роли
    role_permissions = {
        User.Role.CREATOR: [
            'can_export_pdf', 'can_export_json', 'view_public_templates',
            'change_cardtemplate', 'delete_cardtemplate'
        ],
        User.Role.EDITOR: [
            'can_export_json', 'view_public_templates', 'change_cardtemplate'
        ],
        User.Role.MODERATOR: [
            'moderate_content', 'view_public_templates', 'change_cardtemplate',
            'delete_cardtemplate'
        ],
        User.Role.ADMIN: [
            'can_export_pdf', 'can_export_json', 'moderate_content',
            'view_public_templates', 'change_cardtemplate', 'delete_cardtemplate'
        ],
        User.Role.USER: [
            'view_public_templates'
        ],
    }

    required_permissions = role_permissions.get(instance.role, [])
    if not required_permissions:
        return

    # Получаем ContentTypes для моделей
    content_type_template = ContentType.objects.get_for_model(CardTemplate)
    content_type_instance = ContentType.objects.get_for_model(CardInstance)

    # Получаем разрешения, соответствующие кодам
    try:
        needed_permissions = Permission.objects.filter(
            content_type__in=[content_type_template, content_type_instance],
            codename__in=required_permissions
        )
    except Permission.DoesNotExist:
        # Если разрешения еще не созданы, игнорируем
        return

    # Назначаем разрешения пользователю
    instance.user_permissions.set(needed_permissions)