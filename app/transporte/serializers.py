from rest_framework import serializers
from transporte.models import Veiculo, Motorista, Rota


class MotoristaSerializer(serializers.ModelSerializer):
   user_nome = serializers.CharField(source="user.nome", read_only=True)
   user_email = serializers.CharField(source="user.email", read_only=True)
   class Meta:
      model = Motorista
      fields = [
         "id", "user", "user_nome", "user_email", "nome", "telefone", "endereco", "carta_nr", "validade_da_carta", "ativo", "criado_em", "atualizado_em",
      ]


class VeiculoSerializer(serializers.ModelSerializer):
   motorista_nome = serializers.CharField(source="motorista.nome", read_only=True)
   motorista_email = serializers.CharField(source="motorista.user.email", read_only=True)
   vagas_disponiveis = serializers.SerializerMethodField()

   class Meta:
      model = Veiculo
      fields = [
         "id", "marca", "modelo", "matricula", "capacidade", "motorista", "motorista_nome", "motorista_email", "ativo", "criado_em", "atualizado_em", "vagas_disponiveis"
      ]

   def get_vagas_disponiveis(self, obj):
      """assumindo q 0 ocupados pode estar ligado a alunos dpois"""
      ocupados = 0
      # return obj.capacidade - ocupados
      return obj.vagas_desponives(ocupados=ocupados)


class RotaSerializer(serializers.ModelSerializer):
   motorista_nome = serializers.CharField(source="motorista.nome", read_only=True)
   matricula = serializers.CharField(source="veiculo.matricula", read_only=True)
   veiculo_nome = serializers.CharField(source= "veiculo.modelo", read_only=True)
   motorista = serializers.SerializerMethodField()

   class Meta:
       model = Rota
       fields = [
         #  "id", "nome", "descricao", "veiculo", "veiculo_nome", "placa_matricula", "motorista", "ativo", "criado_em", "atualizado_em"
          "id", "nome", "descricao", "veiculo", "veiculo_nome", "matricula", "motorista", "motorista_nome", "hora_partida", "hora_chegada","ativo", "criado_em", "atualizado_em"

       ]
      #  read_only_fields = ("criado_em", "atualizado_em", "motorista", "veiculo_modelo")

   def get_motorista(self, obj):
      """retorna o nome do motorista associado a rota se existir"""
      if obj.veiculo and obj.veiculo.motorista:
         return obj.veiculo.motorista.user.nome
      return None
