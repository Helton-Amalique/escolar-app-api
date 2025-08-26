from rest_framework import serializers
from transporte.models import Veiculo, Motorista, Rota


class MotoristaSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.nome', read_only=True)

    class Meta:
        model = Motorista
        fields = ['id', 'user', 'user_name', 'telefone', 'carta_nr', 'validade_da_carta']

        def get_user_nome(self, obj):
            return getattr(obj.user, 'nome', '')


class VeiculoSerializer(serializers.ModelSerializer):
    motorista = MotoristaSerializer()

    class Meta:
        model = Veiculo
        fields = ['id', 'placa_matricula', 'modelo_carro', 'capacidade', 'motorista']

    def get_motorista_nome(self, obj):
        if obj.motorista and obj.motorista.user:
            return getattr(obj.motorista.user, 'nome', '')
        return None


class RotaSerializer(serializers.ModelSerializer):
    veiculo = VeiculoSerializer(read_only=True)

    class Meta:
        model = Rota
        fields = ['id', 'nome', 'descricao', 'veiculo', 'ativo']

        def get_user_nome(self, obj):
            if obj.veiculo_id:
                return {
                    "placa_matricula": obj.veiculo.placa_matricula,
                    "modelo_carro": obj.veiculo.modelo_carro,
                    "capacidade": obj.veiculo.capacidade,
                }
            return None
