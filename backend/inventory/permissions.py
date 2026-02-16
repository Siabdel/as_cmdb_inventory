"""
Permissions personnalisées pour l'API CMDB Inventory
"""

from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission qui permet l'accès en lecture à tous,
    mais restreint les modifications aux administrateurs.
    """
    
    def has_permission(self, request, view):
        # Autoriser les requêtes GET, HEAD, OPTIONS pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        # Autoriser les modifications uniquement aux administrateurs
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission qui permet l'accès uniquement au propriétaire de l'objet
    ou aux administrateurs.
    """
    
    def has_object_permission(self, request, view, obj):
        # Autoriser les administrateurs
        if request.user.is_staff:
            return True
        # Autoriser le propriétaire de l'objet
        return hasattr(obj, 'created_by') and obj.created_by == request.user


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Permission qui permet l'accès en lecture à tous,
    mais restreint les modifications aux utilisateurs authentifiés.
    """
    
    def has_permission(self, request, view):
        # Autoriser les requêtes GET, HEAD, OPTIONS pour tous
        if request.method in permissions.SAFE_METHODS:
            return True
        # Autoriser les modifications uniquement aux utilisateurs authentifiés
        return request.user and request.user.is_authenticated
