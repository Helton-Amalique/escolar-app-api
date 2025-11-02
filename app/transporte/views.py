from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from transporte.models import Motorista, Veiculo, Rota
from transporte.serializers import MotoristaSerializer, VeiculoSerializer, RotaSerializer

class MotoristaViewSet(viewsets.ModelViewSet):
    queryset = Motorista.objects.all()
    serializer_class = MotoristaSerializer

    permissions_classes = [IsAuthenticated]


class VeiculoViewSet(viewsets.ModelViewSet):
    queryset = Veiculo.objects.all()
    serializer_class = VeiculoSerializer

    permissions_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "perfil_motorista"):
            # Apenas veiculo do motorista logado
            return Veiculo.objects.filter(motorista=user.perfil_motorista, ativo=True)
        return Veiculo.objects.all().order_by("placa_matricula")


class RotaViewSet(viewsets.ModelViewSet):
    queryset = Rota.objects.all()
    serializer_class = RotaSerializer

    permissions_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "perfil_motorista"):
            # Apenas rotas de veivulos do motorista logado
            return Rota.objects.filter(veiculo__motorista=user.perfil_motorista, ativo=True)
        return Rota.objects.nome()









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
