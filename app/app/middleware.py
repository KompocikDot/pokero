# app/app/middleware.py
class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        response['Permissions-Policy'] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )

        if request.user.is_authenticated or request.path.startswith('/admin'):
            response['Cache-Control'] = "no-store, no-cache, must-revalidate, max-age=0"
            response['Pragma'] = "no-cache"


        response['Server'] = "PokeroServer" 

        return response
