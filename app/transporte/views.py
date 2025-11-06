from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from transporte.models import Motorista, Veiculo, Rota
from transporte.serializers import MotoristaSerializer, VeiculoSerializer, RotaSerializer


class MotoristaViewSet(viewsets.ModelViewSet):
    """API para gestão de motoristas"""
    queryset = Motorista.objects.select_related('user').all()
    serializer_class = MotoristaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['ativo']
    search_fields = ['user__nome', 'user__email', 'telefone', 'carta_nr']
    ordering_fields = ['criado_em', 'atualizado_em']


class VeiculoViewSet(viewsets.ModelViewSet):
    """API para gestão de veículos"""
    queryset = Veiculo.objects.select_related('motorista__user').all()
    serializer_class = VeiculoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['ativo', 'motorista']
    search_fields = ['matricula', 'modelo', 'marca', 'motorista__user__nome']
    ordering_fields = ['matricula', 'capacidade', 'criado_em']

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil_motorista'):
            # Apenas veículos do motorista logado
            return Veiculo.objects.filter(motorista=user.perfil_motorista, ativo=True)
        return Veiculo.objects.select_related('motorista__user').all()


class RotaViewSet(viewsets.ModelViewSet):
    """API para gestão de rotas"""
    queryset = Rota.objects.select_related('veiculo__motorista__user').prefetch_related('alunos').all()
    serializer_class = RotaSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['ativo', 'veiculo']
    search_fields = ['nome', 'descricao', 'veiculo__matricula', 'veiculo__modelo']
    ordering_fields = ['nome', 'criado_em', 'hora_partida']

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'perfil_motorista'):
            # Apenas rotas de veículos do motorista logado
            return Rota.objects.filter(veiculo__motorista=user.perfil_motorista, ativo=True)
        return Rota.objects.select_related('veiculo__motorista__user').prefetch_related('alunos').all()









 # o codigo abaixo e funcional
# class MotoristaViewSet(viewsets.ModelViewSet):
#     """API para a gestao de motoristas"""
#     queryset = Motorista.objects.all()
#     serializer_class = MotoristaSerializer
#     Permission_classes = [permissions.IsAuthenticated]
#     filterset_fields = ["ativo"]
#     search_fields = ["user_nome", "user__email", "telefone", "carta_nr"]

#     ordering_fields = ["criado_em", "atualizado_em"]

# class VeiculoViewSet(viewsets.ModelViewSet):
#     """API para gestao de veiculos"""
#     queryset = Veiculo.objects.select_related("motorista").all()
#     serializer_class = VeiculoSerializer
#     Permission_classes = [permissions.IsAuthenticated]
#     filterser_fields = ["ativo", "modelo_carro", "motorista"]
#     search_fields = ["placa_matricula", "modelo_carro", "motorista__user__nome"]
#     ordering_fields = ["placa_matricula", "capacidade"]


# class RotaViewSet(viewsets.ModelViewSet):
#     """API para gestao de rotas"""
#     queryset = Rota.objects.select_related("veiculo", "veiculo__motorista").all()
#     serializer_class = RotaSerializer
#     Permission_classes = [permissions.IsAuthenticated]
#     filterset_fields = ["ativo", "veiculo"]
#     search_fields = ["name", "descricao", "veiculo__placa_marticula", "veiculo__modelo_carro"]
#     ordering_fields = ["nome", "criado_em"]
