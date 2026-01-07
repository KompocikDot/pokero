# app/app/middleware.py
class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        response['Permissions-Policy'] = "accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()"
        
        if request.user.is_authenticated or request.path.startswith('/admin'):
            response['Cache-Control'] = "no-store, no-cache, must-revalidate, max-age=0"
            response['Pragma'] = "no-cache"

        # 3. Ukrywanie wersji serwera (Server Leaks Version)
        # Niestety Gunicorn/Uvicorn często nadpisują to później, ale warto spróbować.
        # W kontenerze to i tak mało istotne, bo nie zdradzamy wersji OS.
        response['Server'] = "PokeroServer" 

        return response
