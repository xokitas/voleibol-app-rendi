from rest_framework import serializers
from .models import (
    Game_Info, Set, Rally, Play, Player, Team, Athlete
)

# Importamos los choices del modelo Play para validación exacta
from .models import Play as PlayModel  # alias para no confundir

# ==================== ENTRADA (validación del JSON) ====================
class MatchPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['number', 'fullName', 'position', 'zone']

class MatchTeamSerializer(serializers.Serializer):
    name = serializers.CharField()
    players = MatchPlayerSerializer(many=True)

class MatchConfigSerializer(serializers.Serializer):
    tournament = serializers.CharField()
    category = serializers.CharField()
    date = serializers.CharField()
    matchNumber = serializers.IntegerField()
    gender = serializers.CharField()
    eventType = serializers.CharField()
    startTime = serializers.CharField(required=False, allow_blank=True)
    place = serializers.CharField(required=False, allow_blank=True)
    denomination = serializers.CharField(required=False, allow_blank=True)
    meso = serializers.CharField(required=False, allow_blank=True)
    micro = serializers.CharField(required=False, allow_blank=True)
    weekDay = serializers.CharField(required=False, allow_blank=True)
    microNumber = serializers.CharField(required=False, allow_blank=True)
    objective = serializers.CharField(required=False, allow_blank=True)
    teamA = MatchTeamSerializer()
    teamB = MatchTeamSerializer()
    platform = serializers.CharField(required=False, allow_blank=True)
    createdBy = serializers.CharField(required=False, allow_blank=True)

class RallyActionSerializer(serializers.Serializer):
    # Ahora validamos contra las opciones del modelo
    category = serializers.ChoiceField(choices=PlayModel.ACTION_CHOICES)
    subAction = serializers.ChoiceField(choices=PlayModel.SUB_ACTION_CHOICES)
    playerId = serializers.CharField()
    value = serializers.IntegerField(required=False, allow_null=True)
    origin = serializers.CharField(required=False, allow_blank=True)
    destination = serializers.CharField(required=False, allow_blank=True)
    wind = serializers.ChoiceField(
        choices=PlayModel.WIND_CHOICES,
        required=False,
        allow_blank=True
    )
    timestamp = serializers.CharField(required=False, allow_blank=True)

class RallySerializer(serializers.Serializer):
    winner = serializers.CharField(required=False, allow_blank=True)
    scoreAtTheTime = serializers.DictField()
    actions = RallyActionSerializer(many=True)

class SetHistorySerializer(serializers.Serializer):
    set = serializers.IntegerField()
    rallies = RallySerializer(many=True)

class MatchScoreSerializer(serializers.Serializer):
    setsA = serializers.IntegerField()
    setsB = serializers.IntegerField()
    pointsA = serializers.IntegerField()
    pointsB = serializers.IntegerField()
    currentSet = serializers.IntegerField()

class MatchSerializer(serializers.Serializer):
    id = serializers.CharField()
    config = MatchConfigSerializer()
    score = MatchScoreSerializer()
    history = SetHistorySerializer(many=True)
    totalTimeSeconds = serializers.IntegerField(required=False, allow_null=True)
    realTimeSeconds = serializers.IntegerField(required=False, allow_null=True)


# ==================== SALIDA (reconstrucción del JSON) ====================
# Los serializadores de salida ya mapean correctamente los campos de la BD,
# así que no necesitan cambios.

class PlayOutputSerializer(serializers.ModelSerializer):
    playerId = serializers.SerializerMethodField()
    category = serializers.CharField(source='action_type')
    subAction = serializers.CharField(source='sub_action')
    value = serializers.IntegerField(source='evaluation')
    origin = serializers.CharField(source='origin_zone')
    destination = serializers.CharField(source='target_zone')

    class Meta:
        model = Play
        fields = ['playerId', 'category', 'subAction', 'value', 'origin', 'destination', 'wind', 'timestamp']

    def get_playerId(self, obj):
        game = obj.rally.set.game
        prefix = 'A' if obj.team == game.team_a else 'B'
        return f"{prefix}-{obj.player.number}"


class RallyOutputSerializer(serializers.ModelSerializer):
    scoreAtTheTime = serializers.SerializerMethodField()
    actions = PlayOutputSerializer(many=True, source='plays')

    class Meta:
        model = Rally
        fields = ['winner', 'scoreAtTheTime', 'actions']

    def get_scoreAtTheTime(self, obj):
        return {'A': obj.score_a, 'B': obj.score_b}


class SetOutputSerializer(serializers.ModelSerializer):
    set = serializers.IntegerField(source='set_number')
    rallies = RallyOutputSerializer(many=True)

    class Meta:
        model = Set
        fields = ['set', 'rallies']


class GameOutputSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='pk')
    config = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()
    status = serializers.CharField()


    class Meta:
        model = Game_Info
        fields = ['id', 'config', 'score', 'history', 'totalTimeSeconds', 'realTimeSeconds', 'status']

    def get_config(self, obj):
        return {
            'tournament': obj.tournament,
            'category': obj.category,
            'date': obj.date,
            'matchNumber': obj.matchNumber,
            'gender': obj.gender,
            'eventType': obj.eventType,
            'startTime': obj.startTime,
            'place': obj.place,
            'denomination': obj.denomination,
            'meso': obj.meso,
            'micro': obj.micro,
            'weekDay': obj.weekDay,
            'microNumber': obj.microNumber,
            'objective': obj.objective,
            'teamA': {
                'name': obj.team_a.name,
                'players': list(obj.team_a.players.values('number', 'fullName', 'position', 'zone'))
            },
            'teamB': {
                'name': obj.team_b.name,
                'players': list(obj.team_b.players.values('number', 'fullName', 'position', 'zone'))
            },
            'platform': obj.platform,
            'createdBy': obj.createdBy,
        }

    def get_score(self, obj):
        return {
            'setsA': obj.setsA,
            'setsB': obj.setsB,
            'pointsA': obj.pointsA,
            'pointsB': obj.pointsB,
            'currentSet': obj.currentSet,
        }

    def get_history(self, obj):
        sets = obj.sets.all().order_by('set_number')
        return SetOutputSerializer(sets, many=True).data


# Serializadores para los ViewSets existentes (sin cambios)
class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = '__all__'

class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Athlete
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class SetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Set
        fields = '__all__'

class GameInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game_Info
        fields = '__all__'

