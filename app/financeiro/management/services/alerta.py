from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from financeiro.models import AlertaEnviado, Pagamento
from collections import defaultdict


def enviar_alerta(p):
    """Envia alerta aos encarregados sobre os pagamentos atrasados"""

    hoje = timezone.now().date()
    # nao envia aleerta antes do dia 10
    if hoje.day < 10:
        return[]

    p_dia = hoje.replace(day=1)

    atrasados = Pagamento.objects.filter(
        status='PENDENTE',
        mes_referente__lt=p_dia
    ).select_related("aluno__encarregado")

    resultados = []
    email_por_encarregado = defaultdict(list)

    for p in atrasados:
        aluno = p.aluno
        encarregado = getattr(aluno, "encarregado", None)
        if encarregado and encarregado.email:
            email_por_encarregado[encarregado].append(p)

    for encarregado, pagamento in email_por_encarregado.items():
        linhas = [
            f"{p.aluno.nome}: {p.valor:.2f} MTN (referente a {p.mes_referente.strftime('%B/%Y')})"
            for p in pagamento
        ]

        mensagem = (
            f"Olá {encarregado.nome},\n\n"
            f"Verificamos que existem pagamento(s) em atraso dos dues educando(s):\n\n"
            + "\n".join(linhas)
            +"\n\nPor favor, regularize o(s) pagamento(s) o mais breve possível."
        )

        try:
            send_mail(
                f"pagamento em atraso - {encarregado.nome}",
                mensagem,
                settings.DEFAULT_FROM_EMAIL,
                [encarregado.email],
            )
            resultados.append((encarregado.nome, encarregado.email, "ENVIADO"))
            """salva log no db"""
            AlertaEnviado.objects.create(
                encarregado=encarregado,
                email=encarregado.email,
                mensagem=mensagem,
                status="ENVIADO"
            )
        except Exception as e:
            resultados.append((encarregado.nome, encarregado.email, f"ERRO: {e}"))
            AlertaEnviado.objects.create(
                encarregado=encarregado,
                email=encarregado.email,
                mensagem=mensagem,
                status=f"ERRO: {e}"
            )
    return resultados
