"""Models para base de dados de Financeiro"""
from django.db import models
from django.conf import settings
from datetime import date, datetime
from decimal import Decimal
from django.utils import timezone
from alunos.models import Aluno, Encarregado
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class StatusMixin(models.Model):
    status = models.CharField(
        max_length=20,
        choices=[("PAGO", "Pago"), ("PENDENTE", "Pendente"), ("ATRASADO", "Atrasado")],
        default="PENDENTE"
    )
    data_pagamento = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def atualizar_status(self):
        """Regras automáticas para status"""
        hoje = date.today()

        if self.status == "PAGO":
            if not self.data_pagamento:
                self.data_pagamento = timezone.now()
        else:
            vencimento = self.mes_referente.replace(day=10)
            if hoje > vencimento and self.status == "PENDENTE":
                self.status = "ATRASADO"
            self.data_pagamento = None
        # return self

    def save(self, *args, **kwargs):
        self.atualizar_status()
        super().save(*args, **kwargs)


class Pagamento(StatusMixin):
    aluno = models.ForeignKey(
        'alunos.Aluno',
        on_delete=models.CASCADE,
        related_name='pagamentos'
    )
    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.0'))],
        null=True, blank=True)
    mes_referente = models.DateField("mes de referencia")

    def clean(self):
        if self.data_pagamento and self.data_pagamento > date.today():
            raise ValidationError(" a data de pagamento nao pode ser no futuro")

        if Pagamento.objects.filter(aluno=self.aluno, mes_referente=self.mes_referente).exclude(pk=self.pk).exists():
            raise ValidationError("Ja existe um pagamento para ese aluno neste mes")

    class Meta:
        unique_together = ('aluno', 'mes_referente')

    def __str__(self):
        return f'{self.aluno.nome} - {self.valor} - {self.mes_referente} - {self.status}'


class Salario(StatusMixin):
    """Pagamento de salario para o funcionarios"""
    funcionario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['FUNCIONARIO', 'MOTORISTA', 'ADMINISTRADOR']},
        related_name='salarios'
    )

    valor = models.DecimalField(max_digits=10, decimal_places=2)
    mes_referente = models.DateField("Mes de referencia")

    def clean(self):
        if self.data_pagamento and self.data_pagamento > date.today():
            raise ValidationError("Data de pagamento nao pode ser no futoro.")

    def __str__(self):
        return f'{self.funcionario.nome} - {self.valor} - {self.mes_referente} - {self.status}'


class AlertaEnviado(models.Model):
    """Alerta enviados para os encarregados"""
    encarregado = models.ForeignKey(
        Encarregado,
        on_delete=models.CASCADE,
        related_name='alertas'
    )
    alunos = models.ManyToManyField(
        Aluno,
        related_name="alerta_enviados"
    )
    email = models.EmailField()
    mensagem = models.TextField()
    enviado_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="ENVIADO")

    def clean(self):
        if not self.email:
            raise ValidationError("O email do encarregado e obrigatorio para envio de alerta.")

        if not self.enviado_em and self.enviado_em > date.today():
            raise ValidationError("A data de envio nao pode ser no futuro.")

        if not self.alunos.count() == 0:
            raise ValidationError("O alerta deve estar associado pelo menis um aluno.")

    def __str__(self):
        # return f"{self.eviado_em.strftime('%d/%m/%Y %H:%M')}"
        return f'Alerta {self.status} para {self.encarregado.user.email}'
