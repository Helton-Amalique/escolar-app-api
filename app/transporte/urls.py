from rest_framework.routers import DefaultRouter
from transporte.views import MotoristaViewSet, VeiculoViewSet, RotaViewSet

router = DefaultRouter()
router.register(r'motorista', MotoristaViewSet)
router.register(r'veiculo', VeiculoViewSet)
router.register(r'rota', RotaViewSet)

urlpatterns = router.urls
