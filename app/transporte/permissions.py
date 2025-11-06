from rest_framework import permissions


class IsAdminOrMotoristaOwner(permissions.BasePermission):
    """
    Permissão customizada:
    - Admin pode tudo
    - Motorista só pode ver/editar seus próprios dados
    """
    
    def has_permission(self, request, view):
        # Usuário precisa estar autenticado
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin tem acesso total
        if request.user.is_staff:
            return True
        
        # Motorista tem acesso limitado
        if hasattr(request.user, 'perfil_motorista'):
            # Só pode listar e visualizar (GET, HEAD, OPTIONS)
            if request.method in permissions.SAFE_METHODS:
                return True
            # Pode editar apenas seus próprios dados
            return view.action in ['update', 'partial_update']
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Admin pode tudo
        if request.user.is_staff:
            return True
        
        # Motorista só pode acessar seus próprios dados
        if hasattr(request.user, 'perfil_motorista'):
            # Para Motorista model
            if hasattr(obj, 'user'):
                return obj.user == request.user
            # Para Veiculo model
            if hasattr(obj, 'motorista'):
                return obj.motorista and obj.motorista.user == request.user
            # Para Rota model
            if hasattr(obj, 'veiculo'):
                return obj.veiculo and obj.veiculo.motorista and obj.veiculo.motorista.user == request.user
        
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permissão que permite:
    - Admin: acesso total
    - Outros usuários autenticados: apenas leitura
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_staff:
            return True
        
        # Apenas métodos seguros (GET, HEAD, OPTIONS) para não-admin
        return request.method in permissions.SAFE_METHODS


class IsMotoristaOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão específica para veículos e rotas:
    - Admin: acesso total
    - Motorista: apenas seus veículos/rotas
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin pode tudo
        if request.user.is_staff:
            return True
        
        # Verificar se é motorista e se o objeto pertence a ele
        if hasattr(request.user, 'perfil_motorista'):
            motorista = request.user.perfil_motorista
            
            # Para Veiculo
            if hasattr(obj, 'motorista'):
                return obj.motorista == motorista
            
            # Para Rota (através do veículo)
            if hasattr(obj, 'veiculo') and obj.veiculo:
                return obj.veiculo.motorista == motorista
        
        return False
