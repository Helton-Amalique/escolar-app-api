"""Models para base de dados de  transporte"""
from django.db import models
from django.conf import settings


class Motorista(models.Model):
    """Informações do/a motorista"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'MOTORISTA'},
        related_name='perfil_motorista'
    )
    telefone = models.CharField(max_length=25, default='sem telefone')
    carta_nr = models.CharField(max_length=50)
    validade_da_carta = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.nome


class Veiculo(models.Model):
    placa_matricula = models.CharField(max_length=20)
    modelo_carro = models.CharField(max_length=100)
    capacidade = models.PositiveIntegerField()
    motorista = models.ForeignKey(
        Motorista,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='veiculos')

    def __str__(self):
        return f'{self.modelo_carro} - {self.placa_matricula}'


class Rota(models.Model):
    """Informações sobre a rota de trasporte"""
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nome
