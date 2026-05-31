from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import (
    Game_Info, Set, Rally, Play, Team, Player, Athlete
)
from .serializers import (
    MatchSerializer, GameOutputSerializer, AthleteSerializer,
    PlaySerializer, TeamSerializer, SetSerializer, GameInfoSerializer
)


class MatchCreateView(APIView):
    """
    Recibe un partido completo (JSON) y lo guarda en la base de datos.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = MatchSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        config = data['config']
        score = data['score']
        history = data['history']

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
            tournament=config.get('tournament', ''),
            category=config.get('category', ''),
            date=config.get('date', ''),
            matchNumber=config.get('matchNumber', 0),
            gender=config.get('gender', 'M'),
            eventType=config.get('eventType', ''),
            startTime=config.get('startTime', None),
            place=config.get('place', None),
            denomination=config.get('denomination', None),
            meso=config.get('meso', None),
            micro=config.get('micro', None),
            weekDay=config.get('weekDay', None),
            microNumber=config.get('microNumber', None),
            objective=config.get('objective', None),
            platform=config.get('platform', None),
            createdBy=request.user.email,
            pointsA=score.get('pointsA', 0),
            pointsB=score.get('pointsB', 0),
            setsA=score.get('setsA', 0),
            setsB=score.get('setsB', 0),
            currentSet=score.get('currentSet', 1),
            totalTimeSeconds=data.get('totalTimeSeconds', None),
            realTimeSeconds=data.get('realTimeSeconds', None),
        )

        for set_data in history:
            set_obj = Set.objects.create(
                game=game,
                set_number=set_data['set'],
            )
            for rally_data in set_data['rallies']:
                score_at_time = rally_data['scoreAtTheTime']
                rally_obj = Rally.objects.create(
                    set=set_obj,
                    winner=rally_data.get('winner', None),
                    score_a=score_at_time.get('A', 0),
                    score_b=score_at_time.get('B', 0),
                )
                for action in rally_data['actions']:
                    player_id = action['playerId']
                    prefix, number = player_id.split('-')
                    team = team_a if prefix == 'A' else team_b
                    player = team.players.filter(number=number).first()
                    if player:
                        Play.objects.create(
                            action_type=action['category'],
                            sub_action=action.get('subAction', ''),
                            evaluation=action.get('value', 0),
                            player=player,
                            team=team,
                            rally=rally_obj,
                            origin_zone=action.get('origin', None),
                            target_zone=action.get('destination', None),
                            timestamp=action.get('timestamp', '00:00'),
                            wind=action.get('wind', None),
                        )

        return Response({'id': game.id}, status=status.HTTP_201_CREATED)


class UserMatchesListView(APIView):
    """
    Devuelve los partidos del usuario autenticado en formato JSON reconstruido.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        games = Game_Info.objects.filter(createdBy=request.user.email)
        serializer = GameOutputSerializer(games, many=True)
        return Response(serializer.data)


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


class MatchDetailView(APIView):
    """
    Actualiza un partido completo (PUT). Solo el creador puede modificarlo.
    """
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, pk):
        try:
            game = Game_Info.objects.get(pk=pk, createdBy=request.user.email)
        except Game_Info.DoesNotExist:
            return Response({"error": "Partido no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        config = data['config']
        score = data['score']
        history = data['history']


        game.tournament = config.get('tournament', '')
        game.category = config.get('category', '')
        game.date = config.get('date', '')
        game.matchNumber = config.get('matchNumber', 0)
        game.gender = config.get('gender', 'M')
        game.eventType = config.get('eventType', '')
        game.startTime = config.get('startTime', None)
        game.place = config.get('place', None)
        game.denomination = config.get('denomination', None)
        game.meso = config.get('meso', None)
        game.micro = config.get('micro', None)
        game.weekDay = config.get('weekDay', None)
        game.microNumber = config.get('microNumber', None)
        game.objective = config.get('objective', None)
        game.platform = config.get('platform', None)
        game.pointsA = score.get('pointsA', 0)
        game.pointsB = score.get('pointsB', 0)
        game.setsA = score.get('setsA', 0)
        game.setsB = score.get('setsB', 0)
        game.currentSet = score.get('currentSet', 1)
        game.totalTimeSeconds = data.get('totalTimeSeconds', None)
        game.realTimeSeconds = data.get('realTimeSeconds', None)
        game.save()

        game.sets.all().delete()


        game.team_a.delete()
        game.team_b.delete()

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
        game.team_a = team_a
        game.team_b = team_b
        game.save()


        for set_data in history:
            set_obj = Set.objects.create(
                game=game,
                set_number=set_data['set'],
            )
            for rally_data in set_data['rallies']:
                score_at_time = rally_data['scoreAtTheTime']
                rally_obj = Rally.objects.create(
                    set=set_obj,
                    winner=rally_data.get('winner', None),
                    score_a=score_at_time.get('A', 0),
                    score_b=score_at_time.get('B', 0),
                )
                for action in rally_data['actions']:
                    player_id = action['playerId']
                    prefix, number = player_id.split('-')
                    team = team_a if prefix == 'A' else team_b
                    player = team.players.filter(number=number).first()
                    if player:
                        Play.objects.create(
                            action_type=action['category'],
                            sub_action=action.get('subAction', ''),
                            evaluation=action.get('value', 0),
                            player=player,
                            team=team,
                            rally=rally_obj,
                            origin_zone=action.get('origin', None),
                            target_zone=action.get('destination', None),
                            timestamp=action.get('timestamp', '00:00'),
                            wind=action.get('wind', None),
                        )

        return Response({'id': game.id}, status=status.HTTP_200_OK)