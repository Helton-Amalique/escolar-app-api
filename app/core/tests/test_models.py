import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
# from django.core.exceptions import ValidationError
# from core.models import Cargo, User

User = get_user_model()


class UserModelTestCase(TestCase):
    # def setUp(self):
    #     self.cargo_dev = Cargo.objects.create(nome="DEV", salario_padrao=Decimal("15000.00"))
    #     self.cargo_admin = Cargo.objects.create(nome="ADMIN", salario_padrao=Decimal("0.00"))
    #     # self.cargo_motorista = Cargo.objects.create(nome="ADMIN", salario_padrao=Decimal("0.00"))
    #     # self.cargo_ = Cargo.objects.create(nome="ADMIN", salario_padrao=Decimal("0.00"))

    # @pytest.mark.django_db
    # def test_criar_usuario_com_salario_padrao(self):
    #     """Usuario sem salario definido deve herdar salario do cargo"""
    #     user = User.objects.create_user(
    #         email="teste@exemplo.com",
    #         nome="Castigo Malate",
    #         role=cargo_dev,
    #         password="senha1233"
    #     )
    #     user.role = cargo_admin
    #     with pytest.raises(ValidationError):
    #         user.save()

    #     self.assertEqual(user.salario, Decimal("15000.00"))

    # @pytest.mark.django_db
    # def test_criar_usuario_costumizado(self):
    #     """User pode ter salario diferente d padrao"""
    #     user = User.objects.create_user(
    #         email="test2@exemplo.com",
    #         nome="Ana Maria",
    #         role=self.cargo_dev,
    #         salario=Decimal("20000.00"),
    #         password="senha1234"
    #     )
    #     self.assertEqual(user.salario, Decimal("20000.00"))

    # @pytest.mark.django_db
    # def test_criar_superuser_com_cargo_admin(self):
    #     """O superuser dever ser criado com cargo ADMIN"""
    #     superuser = User.objects.create_superuser(
    #         email="admin@exemplo.com",
    #         nome='Admim',
    #         password="adminsenha123"
    #     )
    #     self.assertTrue(superuser.is_superuser)
    #     self.assertTrue(superuser.is_staff)
    #     self.assertEqual(superuser.role.nome, "ADMIN")

    # @pytest.mark.django_db
    # def test_email_normalizado(self):
    #     """Email deve ser salvo em minusculas"""
    #     user = User.objects.create_user(
    #         email="TESTEE@EXEMPLO.COM",
    #         nome="Test4",
    #         role=self.cargo_dev,
    #         password="senhaa123"
    #     )
    #     self.assertEqual(user.email, "teste@examplo.com")

    # # class CargoModelTests(TestCase):
    # @pytest.mark.django_db
    # def test_salario_nao_pode_ser_negatico(self):
    #     """Cargp nao deve aceitar salario negativo"""
    #     cargo = Cargo(nome="NEGATIVO", salario_padrao=Decimal("-100.00"))
    #     with pytest.Raises(ValidationError):
    #         cargo.clean()

    def test_cria_usuario(self):
        user = User.objects.create_user(
            email="test@example.com",
            nome="Joao Salomao",
            role="ENCARREGADO",
            password="Senhacommais8"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("Senhacommais8"))
        self.assertEqual(user.role.nome, "ENCARREGADO")
        self.assertTrue(user.is_active)
