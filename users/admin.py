from django.contrib import admin # type: ignore
# Register your models here.
from users.models import User

admin.site.register(User)
