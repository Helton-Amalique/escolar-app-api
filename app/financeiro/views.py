from rest_framework import viewsets, permissions
from .models import Pagamento, Salario, AlertaEnviado
from .serializers import PagamentoSerializer, SalarioSerializer, AlertaEnviadoSerializer


class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all().select_related("aluno")
    serializer_class = PagamentoSerializer
    permission_classes = [permissions.IsAuthenticated]


class SalarioViewSet(viewsets.ModelViewSet):
    queryset = Salario.objects.all().select_related("funcionario")
    serializer_class = SalarioSerializer
    permission_classes = [permissions.IsAuthenticated]


class AlertaEnviadoViewSet(viewsets.ModelViewSet):
    queryset = AlertaEnviado.objects.all().select_related("encarregado").prefetch_related("alunos")
    serializer_class = AlertaEnviadoSerializer
    permission_classes = [permissions.IsAuthenticated]
