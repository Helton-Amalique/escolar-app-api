from rest_framework import viewsets
from transporte.models import Motorista, Veiculo, Rota
from transporte.serializers import MotoristaSerializer, VeiculoSerializer, RotaSerializer


class MotoristaViewSet(viewsets.ModelViewSet):
    queryset = Motorista.objects.all()
    serializer_class = MotoristaSerializer
    filterset_fields = ['telefone']
    search_fields = ['user__nome']


class VeiculoViewSet(viewsets.ModelViewSet):
    queryset = Veiculo.objects.select_related('motorista').all()
    serializer_class = VeiculoSerializer
    filterset_fields = ['modelo_carro', 'capacidade']
    search_fields = ['placa_matricula', 'modelo_carro', 'motorista__user_nome']


class RotaViewSet(viewsets.ModelViewSet):
    queryset = Rota.objects.select_related('veiculo').all()
    serializer_class = RotaSerializer
    filterset_fields = ['ativo']
    search_fields = ['nome', 'veiculo_placa_matricula']
