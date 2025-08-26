from rest_framework.routers import DefaultRouter
from alunos.views import AlunoViewSet, EncarregadoViewSet

router = DefaultRouter()
router.register(r'alunos', AlunoViewSet)
router.register(r'encarregados', EncarregadoViewSet)

urlpatterns = router.urls
