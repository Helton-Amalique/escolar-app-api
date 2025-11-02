"""Models para base de dados de Alunos"""
from django.db import models
from django.conf import settings
from datetime import date
from decimal import Decimal
from django.core.validators import MinValueValidator, EmailValidator, ValidationError
from phonenumber_field.modelfields import PhoneNumberField

validar_email = EmailValidator(message='Degite um email valido')


class Encarregado(models.Model):
    """Pessoa responsavel pelo/a(s) aluno/a(s)"""
    # nome = models.CharField(max_length=255, db_index=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ENCARREGADO'},
        related_name='perfil_encarregado'
    )
    telefone = PhoneNumberField(region="MZ")
    nrBI = models.CharField(max_length=30, blank=False, null=False, help_text="introduza o numero de bilhere de identidade")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    endereco = models.TextField(blank=True, null=True, help_text="bairro, Q, N da casa")

    def __str__(self):
        return getattr(self.user, "nome", str(self.user))


class Aluno(models.Model):
    """Informações de aluno"""
    nome = models.CharField(max_length=255, db_index=True)
    data_nascimento = models.DateField()
    nrBI = models.CharField(max_length=30, blank=False, null=False, help_text="introduza o numero de bilhere de identidade")
    encarregado = models.ForeignKey(
        Encarregado,
        on_delete=models.CASCADE,
        related_name='alunos',
    )
    escola_dest = models.CharField(max_length=255)
    classe = models.CharField(max_length=25)
    rota = models.ForeignKey(
        'transporte.Rota',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    activo = models.BooleanField(default=True, db_index=True)
    mensalidade = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.0'))],
        default=Decimal('0.00')
    )
    email = models.EmailField(
        blank=True,
        null=True,
        validators=[validar_email],
        help_text='Email do aluno e (opcional)',
        db_index=True
    )

    def clean(self):
        hoje = date.today()
        if self.data_nascimento > hoje:
            raise ValidationError({"data_nascimento": "A data de nascimento não pode ser no futuro."})

        idade = hoje.year - self.data_nascimento.year - (
            (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )
        if idade < 3:
            raise ValidationError({"data_nascimento": "O aluno deve ter pelo menos 3 anos."})

    def save(self, *args, **kwargs):
        if self.nome:
            self.nome = self.nome.strip().title()
        if self.escola_dest:
            self.escola_dest = self.escola_dest.strip()
        if self.classe:
            self.classe = self.classe.strip()
        if self.email:
            self.email = self.email.lower().strip()
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
