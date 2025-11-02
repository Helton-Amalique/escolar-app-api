from rest_framework.routers import DefaultRouter
from django.urls import path, include
from transporte.views import MotoristaViewSet, VeiculoViewSet, RotaViewSet

router = DefaultRouter()
router.register(r'motorista', MotoristaViewSet)
router.register(r'veiculo', VeiculoViewSet, basename="veiculo")
router.register(r'rota', RotaViewSet, basename="rota")

urlpatterns = router.urls

urlpatterns = [
    path("api/", include(router.urls)),
]
