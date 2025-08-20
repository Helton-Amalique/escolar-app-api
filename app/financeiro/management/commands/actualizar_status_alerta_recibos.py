from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, datetime
from financeiro.models import Pagamento, Salario
from financeiro.management.services.alerta import enviar_alerta
from financeiro.management.services.recibos import gerar_recibo
from django.core.files.base import ContentFile


class Command(BaseCommand):
    help = "Atualiza status de pagamentos e salários, envia alertas e gera recibos"

    def handle(self, *args, **kwargs):
        hoje = date.today()
        pagos = atrasados = pendentes = alertas_enviados = recibos_gerados = 0

        # --- Atualiza Pagamentos ---
        for p in Pagamento.objects.all():
            if isinstance(p.mes_referente, str):
                try:
                    p.mes_referente = datetime.strptime(p.mes_referente, "%Y-%m-%d").date()
                except ValueError:
                    p.mes_referente = hoje.replace(day=1)

            status_antigo = p.status
            if p.data_pagamento:
                p.status = 'PAGO'
            elif hoje > p.mes_referente.replace(day=10):
                p.status = 'ATRASADO'
            else:
                p.status = 'PENDENTE'
            if p.status != status_antigo:
                p.save()

            # Contagem
            if p.status == 'PAGO':
                pagos += 1
            elif p.status == 'ATRASADO':
                atrasados += 1
            elif p.status == 'PENDENTE':
                pendentes += 1

            # --- Gera Recibo se Pago ---
            if p.status == 'PAGO':
                buffer_pdf = gerar_recibo(p)
                if buffer_pdf:
                    recibos_gerados += 1

        # --- Atualiza Salários ---
        for s in Salario.objects.all():

            # Garantir mes_referente como date
            if isinstance(s.mes_referente, str):
                try:
                    s.mes_referente = datetime.strptime(s.mes_referente, "%Y-%m-%d").date()
                except ValueError:
                    s.mes_referente = hoje.replace(day=1)

            status_antigo = s.status
            if s.data_pagamento:
                s.status = 'PAGO'
            elif hoje > s.mes_referente.replace(day=10):
                s.status = 'ATRASADO'
            else:
                s.status = 'PENDENTE'
            if s.status != status_antigo:
                s.save()

            """# Contagem"""
            if s.status == 'PAGO':
                pagos += 1
            elif s.status == 'ATRASADO':
                atrasados += 1
            elif s.status == 'PENDENTE':
                pendentes += 1

        # --- Envia alertas ---
        pagamentos_alerta = Pagamento.objects.filter(status__in=['PENDENTE', 'ATRASADO'])
        for p in pagamentos_alerta:
            resultado = enviar_alerta(p)
            alertas_enviados += len(resultado) if resultado else 0

        self.stdout.write(self.style.SUCCESS(
            f"Status atualizado: Pagos={pagos}, Atrasados={atrasados}, Pendentes={pendentes}\n"
            f"Alertas enviados: {alertas_enviados}\n"
            f"Recibos gerados: {recibos_gerados}"
        ))
