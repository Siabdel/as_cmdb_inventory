from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from inventory.models import UserProfile
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication

# ── Endpoint pour les utilisateurs avec le rôle 'technicien' ──────────────────────────────────────
class TechnicianUserView(APIView):
    """
    Renvoie la liste des utilisateurs avec le rôle 'technicien'.
    """
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filtrer les utilisateurs avec le rôle 'technicien'
        technician_users = User.objects.filter(profile__role='technician').values(
            'id', 'username', 'email', 'first_name', 'last_name', 'is_staff'
        )
        return Response(list(technician_users))

# ── Endpoint pour récupérer les utilisateurs avec filtre par rôle ──────────────────────────────────────
class FilteredUserView(APIView):
    """
    Renvoie la liste des utilisateurs avec filtre par rôle.
    Supporte le paramètre de requête 'role' (ex: /api/v1/staff/auth/users/?role=technicien)
    """
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.query_params.get('role', None)
        
        if role == 'technicien':
            # Pour le rôle 'technicien', on filtre par le rôle dans le profile
            users = User.objects.filter(profile__role='technician').values(
                'id', 'username', 'email', 'first_name', 'last_name', 'is_staff'
            )
        else:
            # Pour d'autres rôles ou aucun rôle, retourne tous les utilisateurs
            users = User.objects.all().values(
                'id', 'username', 'email', 'first_name', 'last_name', 'is_staff'
            )
        
        return Response(list(users))

# ── Endpoint pour récupérer les informations de l'utilisateur connecté ──────────────────────────────────────
class CurrentUserView(APIView):
    """
    Renvoie les informations de l'utilisateur connecté.
    """
    authentication_classes = [JWTAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        }
        return Response(data)