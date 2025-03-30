from django.core.management import BaseCommand # type: ignore
from users.models import User

class Command(BaseCommand):
    def handle(self, *args, **options):
        admin_user = User.objects.create(
            email='admin@web.top',
            first_name='Admin',
            last_name='Adminov',
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        
        admin_user.set_password('qwerty')
        admin_user.save()
        print('Admin Created')