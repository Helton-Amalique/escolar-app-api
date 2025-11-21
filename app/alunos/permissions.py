from rest_framework import permissions

class IsAdminOrOwner(permissions.BasePermission):
    """
    Permissão personalizada para permitir que apenas administradores ou o próprio usuário
    visualizem ou editem um objeto.
    """
    def has_object_permission(self, request, view, obj):
        # Permite acesso total para administradores
        if request.user and request.user.is_staff:
            return True

        # Permite acesso se o usuário for o "dono" do objeto.
        # Para o Encarregado, o dono é o `user`.
        # Para o Aluno, o dono é o `encarregado.user`.
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'encarregado'):
            return obj.encarregado.user == request.user
        return False
