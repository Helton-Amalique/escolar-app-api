# from rest_framework import viewsets, permitions, decorators, response
# from core.models import User
# # from core.serializers import UserSerializer


# # class IsAdminOrSelf(permitions.BasePermission):
# #     """permite q o admin veja tudo e todos os usuarios vejam a si mesmo"""

# #     def has_obj_permission(self, request, view, obj):
# #         return request.user.role == User.Role.ADMIN or obj == request.user


# # class UserViewSet(viewsets.ModelViewSet):
# #     queryset = User.objects.all()
# #     serializer_class = UserSerializer

# #     def get_permissions(self):
# #         if self.action in ['list', 'destroy']:
# #             return [permitions.IsAdminUser()]
# #         elif self.action in ['retrive', 'update', 'partial_update']:
# #             return [IsAdminOrSelf()]
# #         return [permitions.IsAuthenticated()]

# #     @decorators.action(detail=False, methods=['get'], url_path='me')
# #     def me(self, request):
# #         """Retorna dados do usuario logado"""
# #         serializer = self.get_serializer(request.user)
# #         return response.Response(serializer.data)
