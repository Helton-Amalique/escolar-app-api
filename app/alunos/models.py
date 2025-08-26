"""Models para base de dados de Alunos"""
import re
from django.db import models
from django.conf import settings
from datetime import date
from decimal import Decimal
from django.core.validators import RegexValidator, MinValueValidator, EmailValidator, ValidationError

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
        max_length=20
    )

    def clean(self):
        if self.telefone:
            telefone = self.telefone.strip().replace(" ", "")

            # Normalização: adiciona +258 se não existir
            if telefone.startswith("8") or telefone.startswith("2"):
                telefone = f"+258{telefone}"

            padrao = r"^\+258(8[2-7]\d{7}|2\d{8})$"
            # 8X = móvel | 2X = fixo

            if not re.match(padrao, telefone):
                raise ValidationError({"telefone": "Número inválido. Ex: +258841234567"})

            self.telefone = telefone

    def save(self, *args, **kwargs):
        if self.user:
            self.user = self.user.strip().title()
        self.full_clean()
        super().save(*args, **kwargs)

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
