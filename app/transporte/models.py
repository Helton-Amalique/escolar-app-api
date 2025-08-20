"""Models para base de dados de  transporte"""
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator, EmailValidator

validar_telefone = RegexValidator(
    regex=r'^\+?\d{9}$',
    message='O numero de telefone deve conter apenas digitos e pode iniciar com +. deve 9 digitos'
)

validar_placa = RegexValidator(
    regex=r'^[A-Z]{2,3}-\d{1,4}(-[A-Z]{1,2})?$',
    message='Placa inválida. Ex: ABC-1234 ou ABC-123-XY'
)


class Motorista(models.Model):
    """Informações do/a motorista"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'MOTORISTA'},
        related_name='perfil_motorista'
    )
    telefone = models.CharField(
        max_length=25,
        validators=[validar_telefone],
        help_text="O numero de telefone com 9 digitos",
        db_index=True
    )
    carta_nr = models.CharField(max_length=50, db_index=True)
    validade_da_carta = models.DateField(null=True, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        # return self.user.nome
        return getattr(self.user, "nome", str(self.user))


class Veiculo(models.Model):
    placa_matricula = models.CharField(
        max_length=20,
        unique=True,
        validators=[validar_placa],
        db_index=True
    )
    modelo_carro = models.CharField(max_length=100)
    capacidade = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Numero maximo de Passageiros"
    )
    motorista = models.ForeignKey(
        Motorista,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='veiculos')
    ativo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.modelo_carro = self.modelo_carro.strip()
        self.placa_matricula = self.placa_matricula.strip.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.modelo_carro} - {self.placa_matricula}'


class Rota(models.Model):
    """Informações sobre a rota de transporte"""
    nome = models.CharField(max_length=255)
    descricao = models.TextField(blank=True, null=True)
    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome
