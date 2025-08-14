from django.contrib import admin
from core.admin_mixins.mixins import BaseAdmin
from core.models import User
from alunos.models import Aluno
from financeiro.models import Pagamento, Salario


@admin.register(Pagamento)
class PagamentoAdmin(BaseAdmin):
    list_display = ('aluno', 'mes_referente', 'valor', 'status', 'data_pagamento')
    list_filter = ('status', 'mes_referente')
    search_fields = ('aluno__nome',)

    fieldsets = (
        ('Informacoes do Pagamento das Mensalidades', {
            'fields': ('aluno', 'mes_referente', 'valor', 'status', 'data_pagamento')
        }),
    )


@admin.register(Salario)
class SalarioAdmin(BaseAdmin):
    list_display = ('funcionario', 'mes_referente', 'valor', 'status', 'data_pagamento')
    list_filter = ('mes_referente', 'data_pagamento', 'status')
    search_fields = ('funcionario__nome',)

    fieldsets = (
        ('Informacoes do Pagamento dos Salario', {
            'fields': ('aluno', 'mes_referente', 'valor', 'status', 'data_pagamento')
        }),
    )
