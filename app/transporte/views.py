from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from transporte.models import Motorista, Veiculo, Rota, Aluno, Encarregado
from transporte.serializers import MotoristaSerializer, VeiculoSerializer, RotaSerializer, EncarregadoSerializer
from alunos.serializers import AlunoSerializer


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


class AlunoViewSet(viewsets.ModelViewSet):
    """Api para a gestao de alunos"""
    queryset = Aluno.objects.select_related('encarregado__user', 'rota__veiculo').all()
    serializer_class = AlunoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['ativo', 'classe', 'escola_dest', 'rota']
    search_fields = ['nome', 'nrBI', 'email', 'encarregado__user__nome']
    ordering_fields = ['nome', 'data_nascimento', 'criado_em']

class EncarregadoViewSet(viewsets.ModelViewSet):
    """Api para a gestao de Encarregado"""
    queryset = Encarregado.objects.select_related('user').prefetch_related('alunos').all()
    serializer_class = EncarregadoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['nrBI']
    search_fields = ['user__nome', 'user__email', 'telefone', 'nrBI']
    ordering_fields = ['user__nome', "criado_em"]
