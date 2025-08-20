"""Models para base de dados de Alunos"""

from django.db import models
from django.conf import settings
from decimal import Decimal
from django.core.validators import RegexValidator, MinValueValidator, EmailValidator
# from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)

validar_telefone = RegexValidator(
    regex=r'^\+?\d{9}$',
    message='O numero de telefone deve conter apenas digitos e pode iniciar com +. deve ter 9 digitos'
)

validar_email = EmailValidator(message='Degite um email valido')


class Encarregado(models.Model):
    """Pessoa responsavel pelo/a(s) aluno/a(s)"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'ENCARREGADO'},
        related_name='perfil_encarregado'
    )

    telefone = models.CharField(
        max_length=20,
        validators=[validar_telefone],
        help_text="Numero de telefone com digitos, podemos iniciar com +",
        db_index=True
    )
    endereco = models.TextField(blank=True, null=True, help_text="bairro, Q, N da casa")

    def __str__(self):
        return getattr(self.user, "nome", str(self.user))


class Aluno(models.Model):
    """Informações de aluno"""
    nome = models.CharField(max_length=255, db_index=True)
    data_nascimento = models.DateField()
    encarregado = models.ForeignKey(
        Encarregado,
        on_delete=models.CASCADE,
        related_name='alunos'
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

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if self.nome:
            self.nome = self.nome.sptrip()
        if self.escola_dest:
            self.escola_dest = self.escola_dest.strip()
        if self.classe:
            self.classe = self.classe.strip()
        if self.email:
            self.email = self.email.lower().strip()
        super().save(*args, **kwargs)
