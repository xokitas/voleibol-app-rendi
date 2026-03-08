from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from .models import Athlete, Play, Team, Competition, Set, Game_Info
from .serializers import AthleteSerializer, PlaySerializer, TeamSerializer, SetSerializer, GameInfoSerializer

class AthleteViewSet(viewsets.ModelViewSet):
    """
    API para ver y gestionar Atletas.
    """
    queryset = Athlete.objects.all()
    serializer_class = AthleteSerializer

class PlayViewSet(viewsets.ModelViewSet):
    """
    API para registrar y listar jugadas (acciones de campo).
    """
    queryset = Play.objects.all()
    serializer_class = PlaySerializer
    def create(self, request, *args, **kwargs):
        # Verificamos si lo que llega es una lista [{}, {}] o un objeto solo {}
        is_many = isinstance(request.data, list)
        
        if not is_many:
            return super().create(request, *args, **kwargs)
        
        # Si es una lista, procesamos la creación masiva
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
        # Aquí es donde ocurre la magia: guarda todo de una sola vez
        serializer.save()

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

class SetViewSet(viewsets.ModelViewSet):
    queryset = Set.objects.all()
    serializer_class = SetSerializer

class GameInfoViewSet(viewsets.ModelViewSet):
    queryset = Game_Info.objects.all()
    serializer_class = GameInfoSerializer