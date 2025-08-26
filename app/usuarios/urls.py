# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# from core.views import UserViewSet, RegisterView, PasswordResetRequestView, PasswordRestConfirmView

# router = DefaultRouter()
# router.register(r'usuarios', UserViewSet)

# urlpatterns = [
#     path('', include(router.urls)),

#     path('auth/register/', RegisterView.as_view(), name='register'),
#     path('auth/login/', TokenObtainPairView.as_view(), name='login'),
#     path('auth/refresh/', TokenRefreshView.as_view(), name='refresh'),

#     path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
#     path('auth/password-reset-confirm/<uid>/<token>/' , PasswordRestConfirmView, name='passord_reset_confirm')

# ]
