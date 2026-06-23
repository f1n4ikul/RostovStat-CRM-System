from rest_framework import permissions

class IsModeratorOrAdmin(permissions.BasePermission):
    """Разрешает доступ Модераторам, Админам или персоналу (is_staff)"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Проверяем флаг персонала или роль в профиле
        is_staff = request.user.is_staff
        has_role = False
        if hasattr(request.user, 'profile'):
            has_role = request.user.profile.role in ['moderator', 'admin']
            
        return is_staff or has_role
    
class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Разрешено смотреть всем (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Редактировать или удалять — только автору
        return obj.author == request.user

class IsSystemAdmin(permissions.BasePermission):
    """Разрешает доступ ТОЛЬКО системным администраторам (is_superuser)"""
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Проверяем либо флаг суперпользователя, либо роль admin в профиле
        is_admin_role = False
        if hasattr(request.user, 'profile'):
            is_admin_role = request.user.profile.role == 'admin'
            
        return request.user.is_superuser or is_admin_role