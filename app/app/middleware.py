# app/app/middleware.py

class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Blokujemy dostęp do kamery, mikrofonu, USB itp. (wymóg bezpieczeństwa)
        response['Permissions-Policy'] = "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
        return response
