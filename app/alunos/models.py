""" Models para base de dados de Alunos"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)






class Encarregado(models.Model):
    """Pessoa responsavel pelo/a(s) aluno/a(s)"""
    user= models.OneToOneField(
        settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            limit_choices_to={'role':'ENCARREGADO'},
            related_name='perfil_encarregado'
    )

    telefone = models.CharField(max_length=20)
    endereco = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.nome


class Aluno(models.Model):
    """Informações de aluno"""
    nome = models.CharField(max_length=255)
    data_nascimento = models.DateField()
    encarregado = models.ForeignKey(
        Encarregado,
        on_delete=models.CASCADE,
        related_name='Alunos'
    )
    escola_dest = models.CharField(max_length=255)
    classe = models.CharField(max_length=25)
    rota = models.ForeignKey(
        'transporte.Rota',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome
