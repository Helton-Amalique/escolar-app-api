from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

from rest_framework import viewsets, permissions, decorators, response, generics, status

from core.serializers import UserSerializer, RegisterSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer

User = get_user_model()


class IsAdminOrSelf(permissions.BasePermission):
    """Permite que admin veja todos e usuários vejam apenas a si mesmos"""
    def has_object_permission(self, request, view, obj):
        return request.user.role == User.Role.ADMIN or obj == request.user


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['list', 'destroy']:
            return [permissions.IsAdminUser()]
        elif self.action in ['retrieve', 'update', 'partial_update']:
            return [IsAdminOrSelf()]
        return [permissions.IsAuthenticated()]

    @decorators.action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return response.Response(serializer.data)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return response.Response(
                {"detail": "Se esse email existir no sistema, enviaremos as instruções"},
                status=status.HTTP_200_OK
            )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset_link = f"http://localhost:8000/api/core/auth/password-reset-confirm/{uid}/{token}/"

        send_mail(
            subject="Recuperação de senha",
            message=f"Use este link para redefinir sua senha: {reset_link}",
            from_email="no-reply@meusistema.com",
            recipient_list=[user.email],
        )

        return response.Response(
            {"detail": "Instruções de redefinição enviadas para o email."},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, uid, token):
        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return response.Response(
                {"detail": "Link inválido ou expirado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return response.Response(
                {"detail": "Token inválido ou expirado."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data['new_password']
        user.set_password(new_password)
        user.save()

        return response.Response(
            {"detail": "Senha redefinida com sucesso."},
            status=status.HTTP_200_OK
        )

# from django.core.mail import send_mail
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
# from django.utils.encoding import force_bytes, force_str
# from django.contrib.auth.tokens import default_token_generator
# from django.contrib.auth import get_user_model
# # from core.models import User

# from rest_framework import viewsets, permissions, decorators, response, generics, status

# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# from core.serializers import UserSerializer, RegisterSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer

# User = get_user_model()


# class IsAdminOrSelf(permissions.BasePermission):
#     """permite q o admin veja tudo e todos os usuarios vejam a si mesmo"""
#     def has_obj_permission(self, request, view, obj):
#         return request.user.role == User.Role.ADMIN or obj == request.user


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def get_permissions(self):
#         if self.action in ['list', 'destroy']:
#             return [permissions.IsAdminUser()]
#         elif self.action in ['retrieve', 'update', 'partial_update']:
#             return [IsAdminOrSelf()]
#         return [permissions.IsAuthenticated()]

#     @decorators.action(detail=False, methods=['get'], url_path='me')
#     def me(self, request):
#         """Retorna dados do usuario logado"""
#         serializer = self.get_serializer(request.user)
#         return response.Response(serializer.data)


# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = RegisterSerializer
#     permission_classes = [permissions.AllowAny]


# class PasswordResetRequestView(generics.GenericAPIView):
#     serializer_class = PasswordResetRequestSerializer
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         # return response({'detail': 'Instrucoes de reset enviadas'}, status=status.HTTP_200_OK)
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         email = serializer.validated_data['email']
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return response.Response(
#                 {"detail": "Se esse email existir no sistema, enviaremos as instruções"},
#                 status=status.HTTP_200_OK
#             )

#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         token = default_token_generator.make_token(user)
#         reset_link = f"http://localhost:8000/api/core/auth/password-reset-confirm/{uid}/{token}/"

#         # Envia email (aqui simplificado)
#         send_mail(
#             subject="Recuperação de senha",
#             message=f"Use este link para redefinir sua senha: {reset_link}",
#             from_email="no-reply@meusistema.com",
#             recipient_list=[user.email],
#         )

#         return response.Response(
#             {"detail": "Instruções de redefinição enviadas para o email."},
#             status=status.HTTP_200_OK
#         )

# """Confirma a redifinicao de senha"""
# class PasswordResetConfirmView(generics.GenericAPIView):
#     serializer_class = PasswordResetConfirmSerializer
#     permission_classes = [permissions.AllowAny]

#     def post(self, request, uid, token):
#         # return response({'detail': 'Senha redefinida com succeso'}, status=status.HTTP_200_OK)
#         try:
#             uid = force_str(urlsafe_base64_decode(uid))
#             user = User.objects.get(pk=uid)
#         except (User.DoesNotExist, ValueError, TypeError, OverflowError):
#             return response.Response(
#                 {"detail": "Link inválido ou expirado."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         if not default_token_generator.check_token(user, token):
#             return response.Response(
#                 {"detail": "Token inválido ou expirado."},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         new_password = serializer.validated_data['new_password']
#         user.set_password(new_password)
#         user.save()

#         return response.Response(
#             {"detail": "Senha redefinida com sucesso."},
#             status=status.HTTP_200_OK
#         )
