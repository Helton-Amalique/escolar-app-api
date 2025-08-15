"""financeiro/management/commands/gerar_salarios.py"""

from django.core.management.base import BaseCommand
from core.models import User
from financeiro.models import Salario
from datetime import date


class Command(BaseCommand):
    help = 'Gera salários mensais para Funcionários, Motoristas e Administradores'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mes',
            type=str,
            help='Mês referente no formato YYYY-MM'
        )

    def handle(self, *args, **options):
        mes_str = options.get('mes')
        if mes_str:
            ano, mes = map(int, mes_str.split('-'))
        else:
            hoje = date.today()
            ano, mes = hoje.year, hoje.month

        mes_referente = date(ano, mes, 1)
        total_criados = 0

        usuarios = User.objects.filter(
            role__in=['FUNCIONARIO', 'MOTORISTA', 'ADMINISTRADOR'],
            is_active=True
        )

        for user in usuarios:
            if not Salario.objects.filter(funcionario=user, mes_referente=mes_referente).exists():
                Salario.objects.create(
                    funcionario=user,
                    mes_referente=mes_referente,
                    valor=user.get_salario()
                )
                total_criados += 1
                self.stdout.write(self.style.SUCCESS(f'Salário criado: {user.username} - {user.get_salario()}'))

        self.stdout.write(self.style.SUCCESS(f'Total de salários criados: {total_criados}'))


# class Command(BaseCommand):
#     help = 'Gera Salarios mensais para funcionarios, Motoristas e Admin'

#     def add_arguments(self, parser):
#         parser.add_argument('--mes', type=str, help='Mes referente no formato YYYY-MM')
#         parser.add_argument('--funcionario', type=float, help='Salário de Funcionário')
#         parser.add_argument('--motorista', type=float, help='Salário de Motorista')
#         parser.add_argument('--administrador', type=float, help='Salário de Administrador')
#         parser.add_argument(
#             '--salario_usuario',
#             nargs='*',
#             help='Valores individuais no formato nome:valor (ex: joao:2000 maria:1800)'
#         )

#     def handle(self, *args, **options):
#         mes_str = options.get('mes')
#         if mes_str:
#             ano, mes =map(int, mes_str.split('-'))
#         else:
#             hoje = date.today()
#             ano, mes = hoje.year, hoje.month

#         mes_referente = date(ano, mes, 1)
#         #total_criados = 0

#         salario_individual = {}
#         for s in options.get('salario_usuario', []):
#             try:
#                 name, valor = s.split(':')
#                 salario_individual[nome.strip()] =float(valor.strip())
#             except:
#                 self.stdout.write(self.style.ERROR(f'formato invalido para --salario_usuario': {s}))

#         total_criados = 0
#         total_atualizados = 0

#         for user in User.objects.filter(role_in=['FUNCIONARIO','MOTORISTA','ADMINISTRADOR'], is_active=True)
#             """Determina o valor d salario"""
#             valor = salario_individual.get(user.nome)
#             if valor is None:
#                 """valor padrao por categoria"""
#                 if user.role == 'FUNCIONARIO':
#                     valor = options.get('funcionario', 10000) # exemplo: valor fixo para funcionário
#                 elif user.role == 'MOTORISTA':
#                     valor = options.get('motorista', 15000)  # exemplo: valor fixo para motorista
#                 elif user.role == 'ADMINISTRADOR':
#                     valor = options.get('administrador', 30000)  # exemplo: valor fixo para administrador

#         salario, criado = Salario.objects.get_or_create(
#             funcionario = user,
#             mes_referente=mes_referente,
#             default={'valor': valor}
#         )

#         if criado:
#             total_criados += 1
#             self.stdout.write(self.style.SUCCESS(f'Salario criado: {user.nome} ({user.role}) - MTN {valor}'))
#         else:
#             if salario.valor != valor:
#                 salario.valor = valor
#                 salario.save()
#                 total_atualizados += 1
#                 self.stdout.write(self.style.WARNING(f'Salario actualizada: {user.nome} ({user.role}) - MTN {valor}'))
#             else:
#                 self.stdout.write(f'Salario ja existente e correto: {user.nome} ({user.role}) - MTN {valor}')

#         self.stdout.write(self.style.SUCCESS(f'Total de salario criados: {total_criados}'))
#         self.stdout.write(self.style.SUCCESS(f'Total de salarios actualizados: {total_actualizados}'))
