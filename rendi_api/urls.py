from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.views import AthleteViewSet, PlayViewSet, TeamViewSet, SetViewSet, GameInfoViewSet

# El Router crea las URLs automáticamente (ej: /api/athletes/)
router = DefaultRouter()
router.register(r'athletes', AthleteViewSet)
router.register(r'plays', PlayViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'sets', SetViewSet)
router.register(r'games', GameInfoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)), # Todas las rutas de la API bajo /api/
]