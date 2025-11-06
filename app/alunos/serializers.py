from rest_framework import serializers
from alunos.models import Aluno, Encarregado
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'nome', 'role', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Use o manager do user para criar o usuário e hashear a senha
        password = validated_data.pop("password", None)
        user = self.Meta.model.objects.create_user(**validated_data, password=password)
        return user

    def update(self, instance, validated_data):
        # Atualiza a senha corretamente se ela for fornecida
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        return super().update(instance, validated_data)


class AlunoSerializer(serializers.ModelSerializer):
    idade = serializers.IntegerField(read_only=True)

    class Meta:
        model = Aluno
        fields = (
            "id", "nome", "foto", "idade", "data_nascimento", "nrBI",
            "escola_dest", "classe", "mensalidade",
            "email", "encarregado", "rota", "activo"
        )
        # O encarregado é definido na view, não deve ser passado no payload
        read_only_fields = ("encarregado",)


class EncarregadoSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Encarregado
        fields = ("id", "user", "foto", "telefone", "nrBI", "endereco")

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        # Cria o usuário aninhado usando o UserSerializer
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        # Cria o encarregado e o associa ao usuário
        encarregado = Encarregado.objects.create(user=user, **validated_data)
        return encarregado

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        
        # Atualiza os dados do usuário aninhado
        if user_data:
            user_serializer = UserSerializer(instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
        
        # Atualiza os dados do encarregado
        return super().update(instance, validated_data)
