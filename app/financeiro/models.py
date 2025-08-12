from django.db import models
from django.conf import settings

class Pagamento(models.Model):
    aluno = models.ForeignKey(
        'alunos.Aluno',
        on_delete=models.CASCADE,
        related_name='pagamento'
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    mes_referente = models.CharField(max_length=20)
    data_pagamento = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[("PAGO", "Pago"),("PENDENTE", "Pendente")],
        default="PENDENTE"
    )

    def __str__(self):
        return f'{self.aluno.nome} - {self.mes_referente}'

class Salario(models.Model):
    """Pagamento de salario para o funcionarios"""
    funcionario = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE,
                                    limit_choices_to={'role__in': ['FUNCIONARIO', 'MOTORISTA']},
                                    related_name='salarios')


    valor = models.DecimalField(max_digits=10, decimal_places=2)
    mes_referente = models.CharField(max_length=20)
    data_pagamento = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
         choices=[("PAGO", "Pago"),("PENDENTE", "Pendente")],
        default="PENDENTE"
    )

    def __str__(self):
        return f'{self.funcionario.nome} - {self.mes_referente}'
