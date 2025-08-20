from django.core.management.base import BaseCommand
from alunos.models import Aluno
from core.models import User
from financeiro.models import Pagamento, Salario
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from financeiro.management.services.alerta import enviar_alerta
from financeiro.management.services.recibos import gerar_recibo


class Command(BaseCommand):
    help = 'gerador de pagamentos mensais de alunos ativos e salarios de funcionarios'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mes',
            type=str,
            help='Mes de referente no formato YYYY-MM(ex: 2025-08)'
        )

        parser.add_argument(
            '--forcar',
            action='store_true',
            help='Força atualização mesmo que o pagamento já exista'
        )

    def handle(self, *args, **options):
        hoje = date.today()

        # define mes do referencia
        mes_str = options.get('mes')
        if mes_str:
            try:
                ano, mes = map(int, mes_str.split('-'))
                mes_referente = date(ano, mes, 1)
            except ValueError:
                self.stdout.write(self.style.ERROR('Formato invalido.use YYYY-MM'))
                return
        else:
            # hoje = date.today()
            mes_referente = hoje.replace(day=1)

        forcar = options.get('forcar', False)
        self.stdout.write(f'Gerando pagamentos para o mes {mes_referente.strftime("%Y-%m")}')

        self.gerar_pagementos_alunos(mes_referente, hoje, forcar)

        self.gerar_salarios_funcionarios(mes_referente, hoje, forcar)

        self.stdout.write(self.style.SUCCESS('Processo concluido!'))

        # pagamento de alunos
    def gerar_pagementos_alunos(self, mes_referente, hoje, forcar):
        alunos_activos = Aluno.objects.filter(activo=True)
        for aluno in alunos_activos:
            valor_base = aluno.rota.valor_mensalidade
            valor_total = valor_base

            mes_anterior = (mes_referente - timedelta(days=1)).replace(day=1)
            atraso = Pagamento.objects.filter(
                aluno=aluno,
                mes_referente=mes_anterior,
                status__in=["PENDENTE", "ATRASADO"]
            ).first()
            if atraso:
                valor_total += atraso.valor
                self.stdout.write(self.style.WARNING(
                    f'{aluno.nome} tinha atraso do mes aterior({atraso.valor}) - somado no valor deste mes.'
                ))

            pagamento, criado = Pagamento.objects.get_or_create(
                aluno=aluno,
                mes_referente=mes_referente,
               defaults={'valor': valor_total, 'status': 'PENDENTE'}
                # defaults={'valor': aluno.rota.valor_mensalidade}
            )

            if not criado and forcar:
                pagamento.valor = valor_total
                pagamento.save()
                self.stdout.write(self.style.NOTICE(f'Pagamento atualizado para aluno {aluno.nome} -{pagamento.valor}'))
            elif criado:
                self.stdout.write(self.style.SUCCESS(f'Pagamento criado para aluno {aluno.nome} - {pagamento.valor}'))
            else:
                self.stdout.write(self.style.WARNING(f'Pagamento já existe para aluno {aluno.nome}'))

            # define os prazaos
            vencimento = mes_referente.replace(day=25)
            limite_sem_multa = (mes_referente + relativedelta(months=1)).replace(day=10)

            # aplica multas se passa do limete
            if pagamento.status == "PENDENTE" and hoje > limite_sem_multa:
                multa = pagamento.valor * 0.10
                pagamento.valor += multa
                pagamento.status = "ATRASADO"
                pagamento.save()
                self.stdout.write(self.style.WARNING(f"pagamento de {aluno.nome} ATRASADO. Agrega uma multa de 10% aplicada (+{multa:.2f}).Novo valor: {pagamento.valor}"))

            # gera alerta quando estiver pendente ou atrasado e recibo quando estiver Pago
            if pagamento.status in ['PENDENTE', "ATRASADO"]:
                enviar_alerta(pagamento)
            elif pagamento.status == "PAGO":
                gerar_recibo(pagamento)

        # pagamento de salario dos funcionarios
    def gerar_salarios_funcionarios(self, mes_referente, hoje, forcar):

        funcionarios = User.objects.filter(role__in=['FUNCIONARIO', 'MOTORISTA', 'ADMINISTRADOR'])

        for func in funcionarios:
            valor_base = func.getSalario()
            valor_total = valor_base

            # Verifica salario atrasado do mes anterior
            mes_anterior = (mes_referente - timedelta(days=1).replace(day=1))
            atraso = Salario.objects.filter(
                funcionario=func,
                mes_referente=mes_anterior,
                status__in=["PENDENTE", "ATRASADO"]
            ).first()
            if atraso:
                valor_total += atraso.valor
                self.stdout.write(self.style.WARNING(
                    f"⚠️ {func.nome} tinha salário atrasado ({atraso.valor}) — somado no valor deste mês."
                ))

            # Cria ou actuliza salario do mes
            salario, criado = Salario.objects.get_or_create(
                funcionario=func,
                mes_referente=mes_referente,
                defaults={'valor': valor_total, 'status': "PENDENTE"}
                # default={'valor': func.getSalario()}
            )
            if not criado:
                salario.valor = valor_total
                salario.save()
                self.stdout.write(self.style.NOTICE(f'Salario actualizado para {func.nome} - {salario.valor}'))
            elif criado:
                self.stdout.write(self.style.SUCCESS(f'Salário criado para {func.nome} - {salario.valor}'))
            else:
                self.stdout.write(self.style.WARNING(f'Salário já existe para {func.nome}'))

            # Define limente de pagamento sem multa(10 do mes seguinte)
            limite_sem_multa = (mes_referente + relativedelta(months=1)).replace(day=10)

            if salario.status == "PENDENTE" and hoje > limite_sem_multa:
                salario.status = "ATRASADO"
                salario.save()
                self.stdout.write(self.style.WARNING(f'Salario de {func.nome} marcado como ATRASADO (sem multa). Valor: {salario.valor}'))

            # gera alerta quando sim
            # estiver pendente ou atrasado e recibo quando estiver Pago
            if salario.status in ['PENDENTE', "ATRASADO"]:
                enviar_alerta(salario)
            elif salario.status == "PAGO":
                gerar_recibo(salario)

        # self.stdout.write(self.style.SUCCESS("Processo concluído!"))
