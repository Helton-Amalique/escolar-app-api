from rest_framework import serializers
from transporte.models import Veiculo, Motorista, Rota, Aluno, Encarregado


class MotoristaSerializer(serializers.ModelSerializer):
    user_nome = serializers.CharField(source='user.nome', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.role.nome', read_only=True)

    class Meta:
        model = Motorista
        fields = [
            'id', 'user', 'user_nome', 'user_email', 'user_role',
            'telefone', 'endereco', 'carta_nr', 'validade_da_carta',
            'ativo', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['criado_em', 'atualizado_em']


class VeiculoSerializer(serializers.ModelSerializer):
    motorista_nome = serializers.CharField(source='motorista.user.nome', read_only=True)
    vagas_disponiveis = serializers.IntegerField(read_only=True)

    class Meta:
        model = Veiculo
        fields = [
            'id', 'marca', 'modelo', 'matricula', 'capacidade',
            'motorista', 'motorista_nome', 'vagas_disponiveis',
            'ativo', 'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['vagas_disponiveis', 'criado_em', 'atualizado_em']

    def validate(self, data):
        motorista = data.get('motorista')
        if motorista and not motorista.ativo:
            raise serializers.ValidationError(
                {'motorista': 'Não é possível atribuir um motorista inativo.'}
            )
        return data


class RotaSerializer(serializers.ModelSerializer):
    # Campos read-only aninhados para leitura
    # motorista = serializers.SerializerMethodField(read_only=True)
    motorista_detalhes = serializers.SerializerMethodField(read_only=True)
    veiculo_detalhes = serializers.SerializerMethodField(read_only=True)
    total_alunos = serializers.IntegerField(source='alunos.count', read_only=True)

    # Campo write-only para criação/edição
    veiculo_id = serializers.PrimaryKeyRelatedField(
        queryset=Veiculo.objects.all(),
        source='veiculo',
        write_only=True,
        required=False
    )

    class Meta:
        model = Rota
        fields = [
            'id', 'nome', 'descricao', 'veiculo', 'veiculo_id',
            'veiculo_detalhes', 'motorista_detalhes', 'total_alunos',
            'hora_partida', 'hora_chegada', 'ativo',
            'criado_em', 'atualizado_em'
        ]
        read_only_fields = ['veiculo', 'criado_em', 'atualizado_em']

    def get_motorista_detalhes(self, obj):
        if obj.motorista:
            return {
                'id': obj.motorista.id,
                'user_nome': obj.motorista.user.nome,
                'user_email': obj.motorista.user.email,
                'telefone': str(obj.motorista.telefone)
            }
        return None

    def get_veiculo_detalhes(self, obj):
        if obj.veiculo:
            return {
                'id': obj.veiculo.id,
                'modelo': obj.veiculo.modelo,
                'matricula': obj.veiculo.matricula,
                'capacidade': obj.veiculo.capacidade,
                'vagas_disponiveis': obj.veiculo.vagas_disponiveis
            }
        return None

    def get_total_alunos(self, obj):
        return obj.alunos.count()

    def validate(self, data):
        veiculo = data.get('veiculo')
        if veiculo and not veiculo.motorista:
            raise serializers.ValidationError(
                {'veiculo': 'O veículo selecionado não tem um motorista atribuído.'}
            )
        if veiculo and not veiculo.ativo:
            raise serializers.ValidationError(
                {'veiculo': 'Não é possível criar rota com veículo inativo.'}
            )
        return data


class EncarregadoSerializer(serializers.ModelSerializer):
    user_nome = serializers.CharField(source='user.nome', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_role = serializers.CharField(source='user.role.nome', read_only=True)

    alunos = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Encarregado
        fields = ['id', 'user', 'user_nome', 'user_email', 'user_role', 'telefone', 'nrBI', 'endereco', 'foto', 'alunos', 'criado_em', 'atualizado_em']
        read_only_fields = ['alunos', 'criado_em', 'atualizado_em']

        def get_alunos(self, obj):
            return [
                {
                    'id':aluno.id,
                    'nome':aluno.nome,
                    'classe':aluno.classe,
                    'escola_dest':aluno.escola_dest,
                    'ativo':aluno.ativo,
                }
                for aluno in obj.alunos.all()
            ]

    class AlunoSerializer(serializers.ModelSerializer):
        idade = serializers.IntegerField(read_only=True)
        encarregado_nome = serializers.CharField(source='encarregado.user.nome', read_only=True)
        rota_detalhes = serializers.SerializerMethodField(read_only=True)

        class Meta:
            model = Aluno
            fields = ['id ', 'nome', 'foto', 'data_nascimento', 'idade', 'nrBI', 'encarregado', 'encarregado_nome', 'escola_dest', 'classe', 'rota', 'rota_detalhes', 'ativo', 'email', 'criado_em', 'atualizado_em']
            read_only_fields = ['idade', 'criado_em', 'atualizado_em']

            def get_rota_detalhes(self, obj):
                if obj.rota.id:
                    return {
                        'id':obj.rota.id,
                        'nome':obj.rota.nome,
                        'veiculo':f"{obj.rota.veiculo.modelo} - {obj.rota.veiculo.matricula}" if obj.rota.veiculo else None,
                        'motorista':obj.rota.motorista.user.nome if obj.rota.motorista else None
                    }
                return None