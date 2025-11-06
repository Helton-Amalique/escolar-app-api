"""Models para base de dados de Financeiro"""

from datetime import date
from decimal import Decimal
from django.db import models
from django.db.models import Sum

from django.conf import settings
from django.utils import timezone

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

from alunos.models import Aluno, Encarregado
# from transporte.models import Rota, Veiculo

# from financeiro.utils import gerar_calendario_anual, valor_atualizado, total_pago_funcionario, enviar_recibo_email
from financeiro.tasks import enviar_recibos_individual
from financeiro.managers import MensalidadeManeger, SalarioManeger


CHOICES = [("PAGO", "Pago"), ("PENDENTE", "Pendente"), ("ATRASADO", "Atrasado"), ("PAGO PARCIAL", "Pago Parcial")]
M_PAGAMENTO = [ ("DINHEIRO", "Dinheiro"), ("TRANSFERENCIA", "Transferência"), ("CARTAO", "Cartão"),]


class TimestampMixin(models.Model):
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class StatusMixin(models.Model):

    status = models.CharField(max_length=20, choices=CHOICES,default="PENDENTE")
    data_pagamento = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def atualizar_status(self):
        hoje = date.today()
        if self.status == "PAGO":
            if not self.data_pagamento:
                self.data_pagamento = hoje
        elif hasattr(self, "data_limite") and hoje > self.data_limite:
            self.status = "ATRASADO"


class Mensalidade(TimestampMixin, StatusMixin):
    aluno = models.ForeignKey('alunos.Aluno',on_delete=models.CASCADE,related_name='mensalidades')
    valor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))], blank=True, default=0,)
    mes_referente = models.DateField(help_text="Mes de referencia")
    data_vencimento = models.DateField()
    data_limite = models.DateField(help_text="O ultimo dia permitido para o pagamento")
    taxa_atraso = models.DecimalField(max_digits=5, decimal_places=2, default=0.10, help_text="A taxa de juros incrementa a cada 5 dias(ex:0.10 = 10%)")
    obs = models.TextField(blank=True, null=True)
    recibo_gerado = models.BooleanField(default=False)

    objects = MensalidadeManeger()

    class Meta:
        unique_together = ("aluno", "mes_referente")
        ordering = ["-mes_referente"]

    @property
    def total_pago(self):
        """Soma todos os pagamentos parciais feitos para esta mensalidade."""
        total = self.pagamentos.aggregate(total=Sum('valor'))['total']
        return total or Decimal('0.00')

    @property
    def valor_devido(self):
        """Retorna o valor restante a ser pago."""
        return self.valor_atualizado - self.total_pago

    def atualizar_status(self):
        """
        Calcula e atualiza o status da mensalidade com base nos pagamentos e datas.
        """
        if not self.pk:
            return

        new_status = "PENDENTE"

        total_pago = self.total_pago
        if total_pago >= self.valor_atualizado:
            new_status = "PAGO"
        elif total_pago > 0:
            new_status = "PAGO PARCIAL"
        elif date.today() > self.data_vencimento:
            new_status = "ATRASADO"

        if self.status != new_status:
            self.status = new_status
            fields_to_update = ['status']
            if new_status == "PAGO" and not self.data_pagamento:
                self.data_pagamento = timezone.now()
                fields_to_update.append('data_pagamento')
            self.save(update_fields=fields_to_update)

    def preencher_datas(self, ano: int, mes: int):
       """chama services gerar_calendario_anual pata preencher datas"""
       pass

    @property
    def dias_atraso(self):
        if self.status == "PAGO":
            return 0
        return max((date.today() - self.data_vencimento).days, 0)

    @property
    def valor_atualizado(self):
        """valor atualizado com a multa (pucha do service)"""
        return self.valor

    def clean(self):
        if self.data_limite < self.data_vencimento:
            raise ValidationError("a data limite nao pode ser anterior a data de pagamento")

    def __str__(self):
        try:
            aluno_nome = self.aluno.nome
        except Exception:
            aluno_nome = "Novo Aluno"
        return f"{aluno_nome} - {self.valor:.2f} ({self.status})"


class Pagamento(TimestampMixin):
    """Registra um pagamento (parcial ou total) de uma mensalidade."""
    mensalidade = models.ForeignKey(Mensalidade, on_delete=models.CASCADE, related_name='pagamentos')
    valor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    data_pagamento = models.DateTimeField(default=timezone.now)
    metodo_pagamento = models.CharField(max_length=20, choices=M_PAGAMENTO, default="DINHEIRO")
    observacao = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-data_pagamento']

    def __str__(self):
        return f"Pagamento de {self.valor} para {self.mensalidade.aluno.nome} em {self.data_pagamento.strftime('%d/%m/%Y')}"


class Salario(TimestampMixin, StatusMixin):
    """Pagamento de salario para o funcionarios"""
    funcionario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['FUNCIONARIO', 'MOTORISTA', 'ADMINISTRADOR']},
        related_name='salarios'
    )
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    mes_referente = models.DateField("Mes de referencia", max_length=20)
    obs = models.TextField(blank=True, null=True)
    recibo_gerado = models.BooleanField(default=False)

    objects = SalarioManeger()

    class Meta:
        ordering = ["-mes_referente"]
        verbose_name = "Salario"
        verbose_name_plural = "Salarios"

    @classmethod
    def total_pago_funcionarios(cls, funcion):
        """Total de salarios ja pagos a um funcionario"""
        return cls.objects.filter(funcionario=funcion, status="PAGO").aggregate(total=Sum("valor"))["total"] or Decimal("0.00")

    @classmethod
    def salario_pendente(cls, funcion=None):
        quant = cls.objects.filter(status="PENDENTE")
        # return quant.filter(funcionario=funcion) if funcion else quant
        if funcion:
            quant = quant.filter(funcionario=funcion)
        return quant

    def gerar_recibo_automatico(self):
        """Gera recibo e envia email para o funcionario."""
        if not self.recibo_gerado and self.status == "PAGO":
            self.recibo_gerado = True
            self.save(update_fields=["recibo_gereado"])
            enviar_recibos_individual.delay("salario", self.pk)

    def clean(self):
        """Validacoes antes de salvar"""
        if self.data_pagamento and self.data_pagamento > date.today():
            raise ValidationError("Data de pagamento nao pode ser no futuro.")

    def save(self, *args, **kwargs):
        status_ant = None
        if self.pk:
            status_ant = Salario.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        if self.status == "PAGO" and self.recibo_gerado is False:
            if status_ant != "PAGO":
                self.gerar_recibo_automatico()

    def __str__(self):
        nome_func = getattr(self.funcionario), "nome", str(self.funcionario)
        return f'{nome_func} - {self.valor:.2f} ({self.mes_referente:%m/%Y}) - {self.status}'


class Fatura(StatusMixin):
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal(0.0))])
    data_emissao = models.DateField(default=timezone.now)
    data_vencimento = models.DateField()
    obs = models.TextField(blank=True, null=True)
    recibo_gerado = models.BooleanField(default=False)
    email_destinatario = models.EmailField(help_text=" Email do destinatario da fatura")

    class Meta:
        ordering = ["-data_emissao"]
        verbose_name_plural = "Faturas"


    def gerar_recibo_automatico(self):
        """Dispara task para gerar recibos(service q fara o envio real)"""
        if not self.recibo_gerado and self.status =="PAGO" and self.email_destinatario:
            self.recibo_gerado = True
            self.save(update_fields=["recibo_gerado"])
            enviar_recibos_individual.delay("fatura", self.pk)

    def clean(self):
        if self.data_emissao > date.today():
            raise ValidationError("A data de emissoa nao pode ser no futuro.")
        if self.data_vencimento < self.data_emissao:
            raise ValidationError("A data de vencimento nao pode ser anterior a data de emissao.")
        if self.valor < 0:
            raise ValidationError("O valor da fatura nao pode ser negativo")

    def save(self, *args, **kwargs):
        status_ant = None
        if self.pk:
            status_ant = Fatura.objects.get(pk=self.pk).status

        super().save(*args, **kwargs)

        if self.status == "PAGO" and not self.recibo_gerado and status_ant != "PAGO":
            self.gerar_recibo_automatico()

    def __str__(self):
        return f"{self.descricao} - {self.valor:.2f} ({self.status})"


class AlertaEnviado(TimestampMixin, models.Model):
    """Alerta enviados para os encarregados"""
    TIPO_CHOICES = [
        ("ATRASO","Pagamento em atraso"),
        ("INICIO","Inicio do periodo de pagamento"),
        ("PENDENTE","pagamento pendente"),
        ("OUTRO","Outro"),
    ]

    STATUS_CHOICES = [
        ("ENVIADO","Enviado"),
        ("FALHA NO ENVIO","Falha no envio"),
        ("PENDENTE","Pendente")
    ]

    encarregado = models.ForeignKey(Encarregado,on_delete=models.CASCADE,related_name='alerta_enviados')
    alunos = models.ManyToManyField(Aluno,related_name="alerta_enviados")
    tipo= models.CharField(max_length=20, choices=TIPO_CHOICES, default="OUTRO")
    email = models.EmailField(help_text="Email usado no envio")
    mensagem = models.TextField()
    enviado_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES, default="ENVIADO")

    class Meta:
        ordering = ["-enviado_em"]

    def clean(self):
        if not self.email:
            raise ValidationError("O email do encarregado e obrigatorio para envio de alerta.")
        if not self.mensagem.strip():
            raise ValidationError("A mensagem nao pode ser vazia")
        if self.alunos.count() == 0:
            raise ValidationError("O alerta deve esta associado a pelo menos um aluno")

    def __str__(self):
        # return f"{self.eviado_em.strftime('%d/%m/%Y %H:%M')}"
        return f"Alerta {self.status} - {self.encarregado.user.email} ({self.alunos.count()} alunos)"
