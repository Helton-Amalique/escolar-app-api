from django.core.management.base import BaseCommand
from alunos.models import Aluno
from financeiro.models import Pagamento
from datetime import date


class Command(BaseCommand):
    help = 'pagamento mensais para todos os alunos ativos com opcoes de valor individual'

    def add_arguments(self, parser):

        parser.add_argument(
            '--mes',
            type=str,
            help='Mes referente no formato YYYY-MM'
        )
        parser.add_argument('--valor_padrao', type=float, help='valor padrao de mansalidade caso nao esteje difinido no aluno')

        # examplo de argumento para valor individuais via linha d comando
        parser.add_argument('--valor_aluno', nargs='*', type=str, help='Valores individuais no formato nome:valor')

    def handle(self, *args, **options):
        # define mes do referencia
        mes_str = options.get('mes')
        if mes_str:
            ano, mes = map(int, mes_str.split('-'))
        else:
            hoje = date.today()
            ano, mes = hoje.year, hoje.month

        mes_referente = date(ano, mes, 1)
        valor_padrao = options.get('valor_padrao', 2500)

        valor_individual = {}

        for s in options.get('valor_aluno', []):
            try:
                nome, valor = s.split(':')
                valor_individual[nome.strip()] = float(valor.strip())
            except:
                self.stdout.write(self.style.ERROR(f'Formato invalido para --valor_aluno: {s}. Use nome:valor'))

        total_criados = 0

        for aluno in Aluno.objects.filter(activo=True):
            """Evita duplicar pagamentos do mesmo mes"""
            valor = valor_individual.get(aluno.nome) or aluno.mensalidade or valor_padrao

            # evita duplicar pagamento
            if not Pagamento.objects.filter(aluno=aluno, mes_referente=mes_referente).exists():
                Pagamento.objects.create(
                    aluno=aluno,
                    mes_referente=mes_referente,
                    valor=valor
                )
                total_criados += 1
                self.stdout.write(self.style.SUCCESS(f'Pagamento criado: {aluno.nome} - MTN {valor: 2f}'))
        self.stdout.write(self.style.SUCCESS(f'Total do pagamento criados: {total_criados}'))
