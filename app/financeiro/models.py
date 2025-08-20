"""Models para base de dados de Financeiro"""
from django.db import models
from django.conf import settings
from datetime import date, datetime
from django.utils import timezone


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
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    mes_referente = models.DateField("mes de referencia")

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

    def __str__(self):
        return f'{self.funcionario.nome} - {self.valor} - {self.mes_referente} - {self.status}'
