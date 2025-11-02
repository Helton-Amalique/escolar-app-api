from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError

class Cargo(models.Model):
    """Modelo para armazenar cargo e seus salarios padrao"""
    nome = models.CharField(max_length=50, unique=True)
    salario_padrao = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome

class UserManager(BaseUserManager):

    def create_user(self, email, nome, apelido, role, password=None, **extra_fields):
        """Cria e retorna um usuário comum"""
        if not email:
            raise ValueError('O usuário deve ter um e-mail')
        if not role:
            raise ValueError('O usuário deve ter um papel definido em (role)')

        email = self.normalize_email(email)
        user = self.model(email=email, nome=nome, apelido=apelido, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, apelido, password, **extra_fields):
        # Garante que o cargo admin exista
        admin_role, created = Cargo.objects.get_or_create(nome='ADMIN')

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("O Superusuario deve ter is_staff=true")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("O Superusuario deve ter is_superuser=true")

        # passa a instancia do cargo para create_user
        return self.create_user(email, nome, apelido, role=admin_role, password=password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=30)
    apelido = models.CharField(max_length=30, default="sem apelido")

    role = models.ForeignKey(Cargo, on_delete=models.PROTECT,
                             related_name='Users', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(default=timezone.now, editable=False)
    data_atualizacao = models.DateTimeField(auto_now=True, editable=False)

    salario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Salário do usuário (se vazio, aplica valor padrão do cargo)."
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["nome","apelido", "role"]

    def save(self, *args, **kwargs):
        """
        Define o salário padrão se não for fornecido e impede a alteração do cargo.
        """
        # Impede a alteração do cargo (role) após a criação do usuário.
        if self.pk:
            original_user = User.objects.get(pk=self.pk)
            if original_user.role != self.role:
                raise ValueError("Nao e permitido alterar o cargo do usuario.")

        # Define o salário com base no cargo, se o salário não estiver definido.
        if self.salario is None and self.role and self.role.salario_padrao:
            self.salario = self.role.salario_padrao

        super().save(*args, **kwargs)

    def __str__(self):
        role_name = self.role.nome if self.role else "Sem Cargo"
        return f'{self.nome} ({role_name})'

    def clean(self):
        if not self.role:
            raise ValidationError("O usuario deve ter o papel (role) definido.")
