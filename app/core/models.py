from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):

    def create_user(self, email, nome, role, password=None, **extra_fields):
        """Cria e retorna um usuário comum"""
        if not email:
            raise ValueError('O usuário deve ter um endereço')
        if not role:
            raise ValueError('O usuário deve ter um papel definido em (role)')

        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, nome, password=None, **extra_fields):
        """Cria e retorna super-usuario"""
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('role') != User.Role.ADMIN:
            raise ValueError('O super-usuario deve ter o papel ADMIN')

        return self.create_user(email, nome, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    class Role(models.TextChoices):
        ADMIN = "ADMINISTRADOR", "Administrador"
        FUNCIONARIO = "FUNCIONARIO", "Funcionario"
        MOTORISTA = "MOTORISTA", "Motorista"
        ENCARREGADO = "ENCARREGADO", "Encarregado"

    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True, editable=False)
    data_atualizacao = models.DateTimeField(auto_now=True, editable=False)
    salario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']

    def getSalario(self):
        """retrna salarop individual ou valor padrao de categoria"""
        if self.salario is not None:
            return self.salario

        valores_padrao = {
            'ADMINISTRADOR': 30000,
            'MOTORISTA': 15000,
            'FUNCIONARIO': 10000
        }
        return valores_padrao.get(self.role, 0)

    def __str__(self):
        return f'{self.nome} ({self.get_role_display()})'
