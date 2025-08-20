from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from financeiro.models import Pagamento


def enviar_alerta(p):
    """Envia alerta aos encarregados sobre os pagamentos atrasados"""

    hoje = timezone.now().date()
    # nao envia aleerta antes do dia 10
    if hoje.day < 10:
        return[]

    p_dia = hoje.replace(day=1)
    atrasados = Pagamento.objects.filter(status='PENDENTE', mes_referente__lt=p_dia)
    resultados = []

    for p in atrasados:
        aluno = p.aluno
        encarregado = getattr(aluno, "encarregado", None)

        if encarregado and encarregado.email:
            assunto = f'Pagamento em atraso - {aluno.nome}'
            mensagem = (
                f"Olá {encarregado.nome},\n\n"
                f"Verificamos que o pagamento da mensalidade do aluno {aluno.nome}, "
                f"referente a {p.mes_referente.strftime('%B/%Y')}, ainda não foi efetuado.\n\n"
                f"Valor devido: {p.valor:.2f} MTN.\n\n"
                "Por favor, regularize o pagamento o mais breve possível."
            )

            try:
                send_mail(
                    assunto,
                    mensagem,
                    settings.DEFAULT_FROM_EMAIL,
                    [encarregado.email],
                )
                resultados.append((encarregado.nome, encarregado.email, "ENVIADO"))
            except Exception as e:
                resultados.append((encarregado.nome, encarregado.email, f"ERRO: {e}"))
        else:
            resultados.append((getattr(encarregado, "nome", "N/A"), None, "SEM EMAIL"))

    return resultados
