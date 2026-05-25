from django.shortcuts import render
from django.db import transaction

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import (
    Athlete, Play, Team, Player, Set, Game_Info
)
from .serializers import (
    AthleteSerializer, PlaySerializer, TeamSerializer,
    SetSerializer, GameInfoSerializer, MatchSerializer
)


class MatchCreateView(APIView):
    """
    Recibe un partido completo (JSON) y lo guarda en la base de datos.
    Solo accesible para usuarios autenticados con JWT.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = MatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        config = data['config']

        def crear_equipo(datos_equipo):
            team = Team.objects.create(name=datos_equipo['name'])
            for p in datos_equipo['players']:
                player = Player.objects.create(
                    number=p['number'],
                    fullName=p.get('fullName', ''),
                    position=p.get('position', 'B'),
                    zone=p.get('zone', 'CEN')
                )
                team.players.add(player)
            return team

        team_a = crear_equipo(config['teamA'])
        team_b = crear_equipo(config['teamB'])

        game = Game_Info.objects.create(
            status='IN_PROGRESS',
            team_a=team_a,
            team_b=team_b,
            final_score_a=0,
            final_score_b=0
        )
        # Aquí más adelante podrás guardar los rallies y acciones

        return Response({'id': game.id}, status=status.HTTP_201_CREATED)


class AthleteViewSet(viewsets.ModelViewSet):
    queryset = Athlete.objects.all()
    serializer_class = AthleteSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer

    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)
        if not is_many:
            return super().create(request, *args, **kwargs)

        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_bulk_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_bulk_create(self, serializer):
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