# financeiro/views.py
from rest_framework import viewsets, permissions, decorators, response
from financeiro.models import Mensalidade, Pagamento, Salario, Fatura, AlertaEnviado
from financeiro.serializers import (
    MensalidadeSerializer,
    PagamentoSerializer,
    SalarioSerializer,
    FaturaSerializer,
    AlertaEnviadoSerializer,
)


class MensalidadeViewSet(viewsets.ModelViewSet):
    queryset = Mensalidade.objects.all()
    serializer_class = MensalidadeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.atualizar_status()

    @decorators.action(detail=False, methods=["get"])
    def pendentes(self, request):
        qs = Mensalidade.objects.pendentes()
        return response.Response(MensalidadeSerializer(qs, many=True).data)

    @decorators.action(detail=False, methods=["get"])
    def atrasadas(self, request):
        qs = Mensalidade.objects.atrasadas()
        return response.Response(MensalidadeSerializer(qs, many=True).data)

    @decorators.action(detail=False, methods=["get"])
    def pagas(self, request):
        qs = Mensalidade.objects.pagas()
        return response.Response(MensalidadeSerializer(qs, many=True).data)


class PagamentoViewSet(viewsets.ModelViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        pagamento = serializer.save()
        pagamento.mensalidade.atualizar_status()


class SalarioViewSet(viewsets.ModelViewSet):
    queryset = Salario.objects.all()
    serializer_class = SalarioSerializer
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=["get"])
    def pagos(self, request):
        qs = Salario.objects.pagos()
        return response.Response(SalarioSerializer(qs, many=True).data)

    @decorators.action(detail=False, methods=["get"])
    def pendentes(self, request):
        qs = Salario.objects.pendentes()
        return response.Response(SalarioSerializer(qs, many=True).data)


class FaturaViewSet(viewsets.ModelViewSet):
    queryset = Fatura.objects.all()
    serializer_class = FaturaSerializer
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=["get"])
    def vencidas(self, request):
        qs = Fatura.objects.vencidas()
        return response.Response(FaturaSerializer(qs, many=True).data)

    @decorators.action(detail=False, methods=["get"])
    def pagas(self, request):
        qs = Fatura.objects.pagas()
        return response.Response(FaturaSerializer(qs, many=True).data)

    @decorators.action(detail=False, methods=["get"])
    def pendentes(self, request):
        qs = Fatura.objects.pendentes()
        return response.Response(FaturaSerializer(qs, many=True).data)


class AlertaEnviadoViewSet(viewsets.ModelViewSet):
    queryset = AlertaEnviado.objects.all()
    serializer_class = AlertaEnviadoSerializer
    permission_classes = [permissions.IsAuthenticated]

    @decorators.action(detail=False, methods=["get"])
    def enviados(self, request):
        qs = AlertaEnviado.objects.enviados()
        return response.Response(AlertaEnviadoSerializer(qs, many=True).data)

    @decorators.action(detail=False, methods=["get"])
    def falhos(self, request):
        qs = AlertaEnviado.objects.falhos()
        return response.Response(AlertaEnviadoSerializer(qs, many=True).data)

    @decorators.action(detail=False, methods=["get"])
    def pendentes(self, request):
        qs = AlertaEnviado.objects.pendentes()
        return response.Response(AlertaEnviadoSerializer(qs, many=True).data)



# from rest_framework import viewsets
# from rest_framework.response import Response
# from rest_framework import status

# class PagamentoViewSet(viewsets.ViewSet):
#     """
#     ViewSet temporário para Pagamentos
#     """
#     def list(self, request):
#         return Response({"mensagem": "Listagem de pagamentos"}, status=status.HTTP_200_OK)

# class DespesaViewSet(viewsets.ViewSet):
#     """
#     ViewSet temporário para Despesas
#     """
#     def list(self, request):
#         return Response({"mensagem": "Listagem de despesas"}, status=status.HTTP_200_OK)

# class ReceitaViewSet(viewsets.ViewSet):
#     """
#     ViewSet temporário para Receitas
#     """
#     def list(self, request):
#         return Response({"mensagem": "Listagem de receitas"}, status=status.HTTP_200_OK)
