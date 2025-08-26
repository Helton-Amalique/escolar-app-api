from rest_framework import serializers
from alunos.models import Aluno, Encarregado


class EncarregadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Encarregado
        # fields = '__all__'
        fields = ['id', 'user', 'telefone', 'endereco']


class AlunoSerializer(serializers.ModelSerializer):
    encarregado = EncarregadoSerializer(read_only=True)

    class Meta:
        model = Aluno
        fields = ['id', 'nome', 'data_nascimento', 'encarregado', 'escola_dest', 'classe', 'rota', 'activo', 'mensalidade', 'email']
