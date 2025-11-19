from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal

class Cargo(models.Model):
    """Modelo para armazenar cargo e seus salarios padrao"""
    nome = models.CharField(max_length=50, unique=True)
    salario_padrao = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])

    def clean(self):
        super().clean()
        # if not self.role:
            # raise ValidationError("O ususario deve ter papel (role) definido")
        if self.salario_padrao is not None and self.salario_padrao < Decimal('0.00'):
            raise ValidationError({"Salario": "salario nao pode ser negativo"})

    def __str__(self):
        return self.nome

class UserManager(BaseUserManager):
    def create_user(self, email, nome, role=None, password=None, **extra_fields):
        """Cria e retorna um usuário comum"""
        if not email:
            raise ValueError('O usuário deve ter um e-mail')
        if not role:
            raise ValueError('O usuário deve ter um papel definido em (role)')

        # Aceita role como string (nome do Cargo) ou como instância
        if isinstance(role, str):
            try:
                role = Cargo.objects.get(nome=role)
            except Cargo.DoesNotExist:
                raise ValueError(f"O Cargo '{role}' não existe. Crie o cargo antes de associá-lo a um usuário.")

        email = self.normalize_email(email).lower()
        user = self.model(email=email, nome=nome, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome, password=None, **extra_fields):
        # Garante que o cargo admin exista
        # admin_role, created = Cargo.objects.get_or_create(nome='ADMIN')

        admin_role, _ = Cargo.objects.get_or_create(nome='ADMIN', defaults={'salario_padrao': Decimal('0.00')})

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        # if extra_fields.get("is_staff") is not True:
        #     raise ValueError("O Superusuario deve ter is_staff=true")
        # if extra_fields.get("is_superuser") is not True:
        #     raise ValueError("O Superusuario deve ter is_superuser=true")

        # passa a instancia do cargo para create_user
        return self.create_user(email=email, nome=nome, role=admin_role, password=password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=30)
    role = models.ForeignKey(Cargo, on_delete=models.PROTECT,
                             related_name='Users', null=True, blank=True)

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
    REQUIRED_FIELDS = ["nome"]

    def save(self, *args, **kwargs):
        """
        Define o salário padrão se não for fornecido e impede a alteração do cargo.
        """
        # if self.pk:
        #     original_user = User.objects.get(pk=self.pk)
        #     if original_user.role != self.role:
        #         raise ValidationError({"role": "Nao e permitido alterar o cargo do usuario."})

        if self.pk:
            original_role = User.objects.filter(pk=self.pk).values_list("role_id", flat=True).first()
            if original_role != self.role_id:
                raise ValidationError({"role": "Nao e permitido alterar o cargo do usuario."})


        # Normaliza email
        if self.email:
            self.email = self.email.strip().lower()

        # Define o salário com base no cargo, se o salário não estiver definido.
        if self.salario is None and self.role and self.role.salario_padrao:
            self.salario = self.role.salario_padrao

        super().save(*args, **kwargs)

    def __str__(self):
        role_name = self.role.nome if self.role else "Sem Cargo"
        return f'{self.nome} ({role_name})'

    def alterar_cargo(self, novo_cargo):
        raise ValidationError("Alteracao de cargo deve ser feita via processo adiministrativo")

    # def clean(self):
    #     if not self.role:
    #         raise ValidationError("O usuario deve ter o papel (role) definido.")
