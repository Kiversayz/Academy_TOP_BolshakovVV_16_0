class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Устанавливаем роль только для аутентифицированных пользователей
        if request.user.is_authenticated:
            request.user_role = request.user.role
        else:
            # Для неаутентифицированных пользователей роль не устанавливается
            request.user_role = None

        response = self.get_response(request)
        return response