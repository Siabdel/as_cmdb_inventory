"""
Middleware d'authentification pour les sections admin
"""
from django.shortcuts import redirect


class AdminAuthMiddleware:
    """
    Middleware pour protéger les sections admin
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Liste des URLs protégées
        protected_urls = [
            ##'/admin/stock/',
            ##'/admin/tickets/',
            ##'/admin/assets/',
            ##'/admin/scanner/',
            '/admin/search/',
        ]
        
        # Ne pas rediriger les URLs de login
        login_urls = [
            '/admin/tickets/login/',
            '/admin/login/',
        ]
        
        # Vérifier si l'URL est protégée et n'est pas une URL de login
        if any(request.path.startswith(url) for url in protected_urls) and not any(request.path.startswith(url) for url in login_urls):
            # Vérifier si l'utilisateur est authentifié (utilisation de hasattr pour éviter l'erreur)
            if not hasattr(request, 'user') or not request.user.is_authenticated:
                # Rediriger vers la page de login avec message
                return redirect('/admin/login/')
        
        response = self.get_response(request)
        return response
        
        response = self.get_response(request)
        return response
        
        response = self.get_response(request)
        return response