from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class UserModelTestCase(TestCase):
    def test_cria_usuario(self):
        user = User.objects.create_user(
            email="test@example.com",
            nome="Joao Lorenco",
            role="ENCARREGADO",
            password="Senhacommais8"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("Senhacommais8"))
        self.assertEqual(user.role, "ENCARREGADO")
        self.assertTrue(user.is_active)
