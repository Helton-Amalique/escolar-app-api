from rest_framework import serializers
from financeiro.models import Mensalidade, Pagamento, Salario, Fatura, AlertaEnviado

class PagamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pagamento
        fields = ['id', 'mensalidade', 'valor', 'data_pagamento', 'metodo_pagamento', 'observacao']

class MensalidadeSerializer(serializers.ModelSerializer):
    pagamentos = PagamentoSerializer(many=True, read_only=True)
    total_pago = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    valor_devido = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    valor_atualizado = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    dias_atraso = serializers.IntegerField(read_only=True)

    class Meta:
        model = Mensalidade
        fields = ['id', 'aluno', 'valor', 'mes_referente', 'data_vencimento', 'data_limite', 'taxa_atraso', 'obs', 'recibo_gerado', 'status', 'data_pagamento', 'pagamento', 'total_pago', 'valor_devido', 'valor_atualizado', 'dias_atraso',]

class SalarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salario
        fields = ['id', 'funcionario', 'valor', 'mes_referente' ,'obs', 'recibo_gerado', 'status', 'data_pagamento',]

class FaturaSerializer(serializers.ModelSerializer):
    class Mote:
        model = Fatura
        fields = ['id', 'descricao', 'valor', 'data_emissao' ,'data_vencimento', 'obs', 'recibo_gerado', 'email_destinatario' ,'status', 'data_pagamento',]

class AlertaEnviadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertaEnviado
        fields = ['id', 'encarregado', 'alunos', 'tipo' ,'email', 'mensagem', 'enviado_em', 'status',]