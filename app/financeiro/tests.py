from datetime import date
from decimal import Decimal
from django.core import mail
from django.test import TestCase
from django.utils import timezone
from alunos.models import Aluno, Encarregado
from django.contrib.auth import get_user_model
from fincanceiro.tasks import enviar_alerta_email
from financeiro.models import Mensalidade, Pagamento, Salario, Fatura, AlertaEnviado

User = get_user_model


class FinanceiroSignalsTasksTest(TestCase):
    def setUp(self):
        # Criar usuario funcionario
        self.funcionario = User.objects.create_user(
            username="func1", email="func1@test.com", role="FUNCIONARIO", password="123"
        )

        # criar encarregado e aluno
        self.encarregado = Encarregado.objects.create(user=User.objects.create_user(
            username="enca1", email="enca1@test.com", password="123"
        ))
        self.aluno = Aluno.objects.create(nome="Aluno Teste", encarregado=self.encarregado)

    def test_pagamento_atualiza_status_mensalidade(self):
        mensalidade = Mensalidade.objects.create(
            Aluno=self.aluno,
            valor=Decimal("1000.00"),
            mes_referente=date.today(),
            data_vencimento=date.today(),
            data_limite=date.today(),
        )
        Pagamento.objects.create(mensalidade=mensalidade, valor=Decimal("1000.00"))
        mensalidade.refresh_from_db()
        self.assertEqual(mensalidade.status, "PAGO")

    def test_salario_gera_recibo(self):
        salario = Salario.objects.create(
            funcionario=self.funcionario,
            valor=Decimal("1500.00"),
            mes_referente=date.today(),
            status="PAGO"
        )
        salario.refresh_from_db()
        self.assertTrue(salario.recibo_gerado)

    def test_fatura_gera_recibo(self):
        fatura = Fatura.objects.create(
            descricao="Servico de transporte",
            valor=Decimal("1550.00"),
            data_emissao=date.today(),
            data_vencimento=date.today(),
            email_destinatario="client@test.com",
            status="PAGO"
        )
        fatura.refresh_from_db()
        self.assertTrue(fatura.recibo_gerado)

    def test_altera_criado_para_mensalidade(self):
        mensalidade = Mensalidade.objects.create(
            aluno=self.aluno,
            valor=Decimal("1000.00"),
            mes_referente=date.today(),
            data_vencimento=date.today(),
            data_limite=date.today(),
        )
        # Forcar status atrasado
        mensalidade.status = "ATRASADO"
        mensalidade.save()
        alerta = AlertaEnviado.objects.last()
        self.assertEqual(alerta.tipo, "ATRASO")
        self.assertEqual(alerta.status, "PENDENTE")

    def test_task_envia_email_alerta(self):
        alerta = AlertaEnviado.objects.create(
            encarregado=self.encarregado,
            email="enca1@test.com",
            mensagem="Teste de alerta",
            tipo="PENDENTE",
            status="PENDENTE"
        )
        enviar_alerta_email(alerta.pk)
        alerta.refresh_from_db()
        self.assertEqual(alerta.status, "ENVIADO")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Teste de alerta", mail.outbox[0].body)
