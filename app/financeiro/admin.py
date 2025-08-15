from django.contrib import admin
from django.utils import timezone
from datetime import date
from django.utils.html import format_html
from core.admin_mixins.mixins import BaseAdmin
from financeiro.models import Pagamento, Salario


class StatusActionMixins:
    """mixin para acoes em massa no admin"""

    def marca_como_pago(self, request, queryset):
        atualizado = queryset.update(status='PAGO', data_pagamento=timezone.now())
        self.message_user(request, f'{atualizado} registros marcados como PAGO.')
    marca_como_pago.short_description = "Marcar comm PAGO"

    def marcar_como_pendente(self, request, queryset):
        atualizado = queryset.update(status='PENDENTE', data_pagamento=None)
        self.message_user(request, f'{atualizado} registros marcados como PENDENTE')
    marcar_como_pendente.short_description = "Marcar como PENDENTE"


class StatusListFilter(admin.SimpleListFilter):
    """Filtro lateral status de pagamentos"""
    title = 'Status Personalizado'
    parameter_name = 'status_custom'

    def lookups(self, request, model_admin):
        return [
            ('PAGO', 'Pagos ✅'),
            ('PENDENTE', 'Pendentes ⏳'),
            ('ATRASADO', 'Atrasados ⛔'),
        ]

    def queryset(self, request, queryset):
        hoje = date.today()
        if self.value() == 'PAGO':
            return queryset.filter(status='PAGO')
        elif self.value() == 'PENDENTE':
            return queryset.filter(status='PENDENTE')
        elif self.value() == 'ATRASADO':
            return queryset.filter(status='PENDENTE', mes_referente__lt=hoje.replace(day=1))
        return queryset


class BasePagamentoAdmin(StatusActionMixins, BaseAdmin):

    list_filter = ('status', 'mes_referente', StatusListFilter)
    readonly_fields = ('data_pagamento',)
    actions = ['marcar_como_pago', 'marcar_como_pendente']

    def status_colorido(self, obj):
        if obj.status == 'PAGO':
            cor = '#d4edda'  # Verde claro
        else:
            hoje = date.today()
            if obj.status == 'PENDENTE' and obj.mes_referente < hoje.replace(day=1):
                cor = '#f8d7da'  # Vermelho claro
            else:
                cor = '#fff3cd'  # Amarelo claro
        return format_html(
            '<span style="background-color: {}; padding: 4px 8px; border-radius: 4px;">{}</span>',
            cor,
            obj.status
        )
    status_colorido.short_description = 'Status'

    def save_model(self, request, obj, form, change):

        """Define valor e data de pagamento automaticamente"""

        if hasattr(obj, 'aluno') and obj.aluno and not obj.valor:
            obj.valor = obj.aluno.rota.valor_mensalidade

        if not obj.valor:
            user = getattr(obj, 'funcionario', None) \
                or getattr(obj, 'motorista', None) \
                or getattr(obj, 'administrador', None)

            if user:
                obj.valor = user.getSalario()

        # Se for pagamento de mensalidade (tem aluno)
        # if hasattr(obj, 'aluno') and obj.aluno and not obj.valor:
        #     obj.valor = obj.aluno.rota.valor_mensalidade  # pega da rota

        # # Se for pagamento de salário (tem funcionario)
        # if hasattr(obj, 'funcionario') and obj.funcionario and not obj.valor:
        #     obj.valor = obj.funcionario.salario_fixo  # pega do campo do funcionário

        # if hasattr(obj, 'motorista') and obj.motorista and not obj.valor:
        #     obj.valor = obj.motorista.salario_fixo

        # if hasattr(obj, 'administrador') and obj.administrador and not obj.valor:
        #     obj.valor = obj.administrador.salario_fixo

        #  Define data e pagamento s status for Pago
        if obj.status == 'PAGO' and obj.data_pagamento is None:
            obj.data_pagamento = timezone.now()
        elif obj.status != 'PAGO':
            obj.data_pagamento = None

        super().save_model(request, obj, form, change)


@admin.register(Pagamento)
class PagamentoAdmin(BasePagamentoAdmin):
    list_display = ('aluno', 'mes_referente', 'valor', 'status', 'data_pagamento')
    list_filter = ('status', 'mes_referente')
    search_fields = ('aluno__nome',)
    readonly_fields = ('data_pagamento',)

    fieldsets = (
        ('Informações do Pagamento das Mensalidades', {
            'fields': ('aluno', 'mes_referente', 'valor', 'status')
        }),
        ('Informações do Sistema', {
            'fields': ('data_pagamento',),
        })
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if 'status__exact' not in request.GET:
            return qs.filter(status='PENDENTE')
        return qs


@admin.register(Salario)
class SalarioAdmin(BaseAdmin):
    list_display = ('funcionario', 'mes_referente', 'valor', 'status', 'data_pagamento')
    list_filter = ('mes_referente', 'data_pagamento', 'status')
    search_fields = ('funcionario__nome',)

    readonly_fields = ('data_pagamento',)

    fieldsets = (
        ('Informacoes do Pagamento dos Salario', {
            'fields': ('funcionario', 'mes_referente', 'valor', 'status', 'data_pagamento')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if 'status__exact' not in request.GET:
            return qs.filter(status='PENDENTE')
        return qs
