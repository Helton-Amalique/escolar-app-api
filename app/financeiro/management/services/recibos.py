from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.http import HttpResponse
from io import BytesIO
from datetime import date


def gerar_recibo(pagamento):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica-Bold", 17)
    p.drawString(200, 800, "RECIBO DE PAGAMENTO")

    p.setFont("Helvetica", 12)

    # nome = (
    #     getattr(pagamento, "Aluno", None) and pagamento.aluno.nome
    # ) or (
    #     getattr(pagamento, "funcionario", None) and pagamento.funcionario.nome
    # ) or (
    #     getattr(pagamento, "motorista", None) and pagamento.motorista.nome
    # ) or (
    #     getattr(pagamento, "administrador", None) and pagamento.administrador.nome
    # ) or "N/A"

    nome = None
    nome = pagamento.aluno.nome
    if getattr(pagamento, "Aluno", None):
        nome = pagamento.aluno.nome
        tipo = "Mensalidade"
    elif getattr(pagamento, "funcionario", None):
        nome = pagamento.funcionario.nome
        tipo = "Salario"
    elif getattr(pagamento, "motorista", None):
        nome = pagamento.motorista.nome
        tipo = "Salario"

    elif getattr(pagamento, "administrador", None):
        nome = pagamento.administrador.nome
        tipo = "Salario"
    else:
        tipo = "N/A"

    p.drawString(50, 750, f" Nome: {nome}")
    p.drawString(50, 730, f" Tipo: {tipo}")
    p.drawString(50, 710, f" Valor: MTN {pagamento.valor: .2f}")
    p.drawString(50, 690, f" Data: {(pagamento.data_pagamento or date.today()).strftime('%d/%m/%Y')}")
    p.drawString(50, 670, f" Status: {pagamento.status}")

    p.drawString(50, 620, 'Assinatura: ______________________ .')

    p.setFont("Helvetica-Oblique", 10)
    p.drawString(180, 40, "Obrigado pela sua colaboração")

    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='apication/pdf')
    response['content-Description'] = f'inline; filename=recibo_{pagamento.id}.pdf'
    return response
