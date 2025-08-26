from rest_framework import serializers
from .models import Pagamento, Salario, AlertaEnviado
from alunos.models import Aluno, Encarregado
from core.models import User


class PagamentoSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.CharField(source="aluno.nome", read_only=True)

    class Meta:
        model = Pagamento
        fields = ["id", "aluno", "aluno_nome", "valor", "mes_referente", "status", "data_pagamento"]
        read_only_fields = ["status", "data_pagamento"]


class SalarioSerializer(serializers.ModelSerializer):
    funcionario_nome = serializers.CharField(source="funcionario.nome", read_only=True)
    funcionario_role = serializers.CharField(source="funcionario.role", read_only=True)

    class Meta:
        model = Salario
        fields = ["id", "funcionario", "funcionario_nome", "funcionario_role",
                  "valor", "mes_referente", "status", "data_pagamento"]
        read_only_fields = ["status", "data_pagamento"]


class AlertaEnviadoSerializer(serializers.ModelSerializer):
    encarregado_nome = serializers.CharField(source="encarregado.user.nome", read_only=True)
    alunos_nomes = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="nome", source="alunos"
    )

    class Meta:
        model = AlertaEnviado
        fields = ["id", "encarregado", "encarregado_nome", "alunos", "alunos_nomes",
                  "email", "mensagem", "enviado_em", "status"]
        read_only_fields = ["enviado_em", "status"]
