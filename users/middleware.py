class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            request.user_role = 'GUEST'
        else:
            request.user_role = request.user.role
            
        response = self.get_response(request)
        return response