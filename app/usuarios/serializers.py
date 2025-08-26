from rest_framework import serializers
from core.models import User


class UserSerializer(serializers.ModelsSerializer):
    class Meta:
        model = User
        feilds = ['id', 'email', 'nome', 'role', 'is_active', 'salario', 'data_criacao', 'data_atualizacao']
        read_only_fields = ['id', 'datacriacao', 'data_atualizacao']
