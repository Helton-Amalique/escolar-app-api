"""Models para base de dados de  transporte"""
from datetime import date, time
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator, EmailValidator



validar_telefone = RegexValidator(
    regex=r'^\+?\d{9}$',
    message='O numero de telefone deve conter apenas digitos e pode iniciar com +. deve 9 digitos'
)

validar_placa = RegexValidator(
    regex=r'^[A-Z]{2,3}-\d{1,4}(-[A-Z]{1,2})?$',
    message='Placa inválida. Ex: ABC-1234 ou ABC-123-XY'
)

class ActivoManeger(models.Manager):
    def ativos(self):
        return self.filter(ativo=True)

class Motorista(models.Model):
    """Informações do/a motorista"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'MOTORISTA'},
        related_name='perfil_motorista'
    )
    nome = models.CharField(max_length=100, null=True, blank=True, help_text="Nome do motorista")
    telefone = models.CharField(max_length=25, validators=[validar_telefone], help_text="O numero de telefone com 9 digitos", db_index=True)
    endereco = models.CharField(max_length=200, blank=True, null=True)

    carta_nr = models.CharField(max_length=50, db_index=True)
    validade_da_carta = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True, null=True)

    objects = ActivoManeger()

    def __str__(self):
        return self.nome or str(self.user)
        # return getattr(self.user, "nome", str(self.user))


    def carta_valida(self):
        """retoran True se a carta de conducao  estiver valida"""
        if self.validade_da_carta:
            return self.validade_da_carta >= date.today()
        return False


class Veiculo(models.Model):
    marca = models.CharField(max_length=20, default="desconhecida")
    modelo = models.CharField(max_length=50, default="desconhecida")
    matricula = models.CharField(max_length=20, unique=True, validators=[validar_placa], db_index=True, help_text="Placa de matricula do veiculo")
    capacidade = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="Numero maximo de Passageiros")
    motorista = models.ForeignKey(
        Motorista,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='veiculos'
        )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True, null=True)

    def save(self, *args, **kwargs):
        self.modelo = self.modelo.strip()
        self.matricula = self.matricula.strip().upper()
        super().save(*args, **kwargs)

    # objects = ActivoManeger()

    def vagas_disponives(self, ocupados=0):
        """retorna o numero de ligares disponives na carrinha"""
        return max(self.capacidade - ocupados, 0)

    def __str__(self):
        return f'{self.modelo} - {self.matricula}'


class Rota(models.Model):
    """Informações sobre a rota da carrinha escolar"""
    nome = models.CharField(max_length=255)
    motorista = models.ForeignKey(Motorista, on_delete=models.SET_NULL, null=True, blank=True, related_name="rotas")
    veiculo = models.ForeignKey(Veiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name="rotas")
    hora_partida = models.TimeField(default=time(6, 0))
    hora_chegada = models.TimeField(default=time(7, 0))
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ["nome"]


    def motorista_atribuido(self):
        """retorna o motorista do veiculo da rota, se houver"""
        return self.veiculo.motorista if self.veiculo else None

    def __str__(self):
        return self.nome
