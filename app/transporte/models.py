"""Models para base de dados de  transporte"""
import datetime
from datetime import date
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator, EmailValidator
from phonenumber_field.modelfields import PhoneNumberField

# validar_telefone = RegexValidator(
#     regex=r'^\+?\d{9}$',
#     message='O numero de telefone deve conter apenas digitos e pode iniciar com +. deve 9 digitos'
# )

validar_placa = RegexValidator(
    regex=r'^[A-Z]{2,3}-\d{1,4}(-[A-Z]{1,2})?$',
    message='Placa inválida. Ex: ABC-1234 ou ABC-123-XY'
)

validar_email =EmailValidator(message="Email invalido")


class ActivoManager(models.Manager):
    def ativos(self):
        return self.filter(ativo=True)


class Motorista(models.Model):
    """Informações do/a motorista"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to=Q(role__nome='MOTORISTA'),
        related_name='perfil_motorista'
    )
    telefone = PhoneNumberField(region="MZ", help_text="O numero de telefone com 9 digitos", db_index=True)
    endereco = models.CharField(max_length=200, blank=True, null=True)

    carta_nr = models.CharField(max_length=50, unique=True, db_index=True)
    validade_da_carta = models.DateField()
    ativo = models.BooleanField(default=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = ActivoManager()

    class Meta:
        verbose_name = 'Motorista'
        verbose_name_plural = 'Motoristas'
        ordering = ['-criado_em']

    def __str__(self):
        return getattr(self.user, "nome", str(self.user))

    def clean(self):
        super().clean()
        if self.validade_da_carta and self.validade_da_carta < date.today():
            raise ValidationError({'validade_da_carta': 'A carta de condução está expirada.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Veiculo(models.Model):
    marca = models.CharField(max_length=20, default="desconhecida")
    modelo = models.CharField(max_length=50, default="desconhecida")
    matricula = models.CharField(max_length=20, unique=True, validators=[validar_placa], db_index=True, help_text="Placa de matricula do veiculo")
    capacidade = models.PositiveIntegerField(validators=[MinValueValidator(1)], help_text="Numero maximo de Passageiros")
    motorista = models.ForeignKey(
        Motorista,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='veiculos'
        )
    ativo = models.BooleanField(default=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = ActivoManager()

    class Meta:
        verbose_name = 'Veículo'
        verbose_name_plural = 'Veículos'
        ordering = ['matricula']

    def save(self, *args, **kwargs):
        if self.marca:
            self.marca = self.marca.strip().title()
        if self.modelo:
            self.modelo = self.modelo.strip().title()
        if self.matricula:
            self.matricula = self.matricula.strip().upper()
        super().save(*args, **kwargs)

    @property
    def vagas_disponiveis(self):
        """Retorna o número de lugares disponíveis no veículo."""
        # Assumindo que a relação inversa de Aluno para Rota é 'alunos'
        # e que o Veiculo so pode ter uma rota
        rota_unica = self.rotas.first()
        if not rota_unica:
            return self.capacidade
        alunos_na_rota = rota_unica.alunos.count()
        return max(self.capacidade - alunos_na_rota, 0)

    def __str__(self):
        return f'{self.modelo} - {self.matricula}'


class Rota(models.Model):
    """Informações sobre a rota da carrinha escolar"""
    nome = models.CharField(max_length=255, db_index=True)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.PROTECT, related_name="rotas")
    hora_partida = models.TimeField(default=datetime.time(6, 0))
    hora_chegada = models.TimeField(default=datetime.time(7, 0))
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rota'
        verbose_name_plural = 'Rotas'
        ordering = ["nome"]

    def clean(self):
        super().clean()
        if self.veiculo and not self.veiculo.motorista:
            raise ValidationError({'veiculo': 'O veículo selecionado não tem um motorista atribuído.'})
        if self.veiculo and not self.veiculo.ativo:
            raise ValidationError({'veiculo': 'O veiculo selecionado esta inativo.'})
        if self.hora_chegada <= self.hora_partida:
            raise ValidationError({'hora_chegada': 'A hora de chegada deve ser posterior a hora de partida.'})

    @property
    def motorista(self):
        """retorna o motorista do veiculo da rota, se houver"""
        return self.veiculo.motorista if self.veiculo else None

    def __str__(self):
        return self.nome


class Encarregado(models.Model):
    """Pessoa responsavel pelo/a(s) aluno/a(s)"""
    # nome = models.CharField(max_length=255, db_index=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to=Q(role__nome='ENCARREGADO'),
        related_name='perfil_encarregado_transporte'
    )
    foto = models.ImageField(upload_to='fotos_encarregados/', blank=True, null=True)
    telefone = PhoneNumberField(region="MZ")
    nrBI = models.CharField(max_length=30, unique=True, blank=False, null=False, help_text="introduza o numero de bilhere de identidade")
    endereco = models.TextField(blank=True, null=True, help_text="bairro, Q, N da casa")

    ativo = models.BooleanField(default=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = ActivoManager()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return getattr(self.user, "nome", str(self.user))

class Aluno(models.Model):
    """Informações de aluno"""
    nome = models.CharField(max_length=255, db_index=True)
    foto = models.ImageField(upload_to='fotos_alunos/', blank=True, null=True)
    data_nascimento = models.DateField()
    nrBI = models.CharField(max_length=30, unique=True, blank=False, null=False, help_text="introduza o numero de bilhere de identidade")
    encarregado = models.ForeignKey(
        Encarregado,
        on_delete=models.CASCADE,
        related_name='alunos_transporte',
    )
    escola_dest = models.CharField(max_length=255)
    classe = models.CharField(max_length=25)
    rota = models.ForeignKey(
        'transporte.Rota',
        on_delete=models.PROTECT,  # Impede que a rota seja apagada se houver alunos nela
        related_name='alunos_transporte',
        null=True,
        blank=True
    )

    ativo = models.BooleanField(default=True, db_index=True)
    mensalidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.0'))],
        default=Decimal('0.00')
    )
    email = models.EmailField(
        blank=True,
        null=True,
        unique=True,
        validators=[validar_email],
        help_text='Email do aluno e (opcional)',
        db_index=True
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    objects = ActivoManager()
    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['nome']

    def clean(self):
        hoje = date.today()
        if self.data_nascimento > hoje:
            raise ValidationError({"data_nascimento": "A data de nascimento não pode ser no futuro."})

        idade = hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )
        if idade < 3:
            raise ValidationError({"data_nascimento": "O aluno deve ter pelo menos 3 anos."})
        if self.ativo and self.mensalidade <= 0:
            raise ValidationError({"mensalidade": "Alunos ativos devem ter a mensalidade definida."})

    def save(self, *args, **kwargs):
        if self.nome:
            self.nome = self.nome.strip().title()
        if self.escola_dest:
            self.escola_dest = self.escola_dest.strip()
        if self.classe:
            self.classe = self.classe.strip()
        if self.email:
            self.email = self.email.lower().strip()
        super().save(*args, **kwargs)
