from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import AthleteViewSet, PlayViewSet, TeamViewSet, SetViewSet, GameInfoViewSet, MatchCreateView

router = DefaultRouter()
router.register(r'athletes', AthleteViewSet)
router.register(r'plays', PlayViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'sets', SetViewSet)
router.register(r'games', GameInfoViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/matches/', MatchCreateView.as_view(), name='match-create'),

]