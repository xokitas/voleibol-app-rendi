from rest_framework import serializers
from .models import Play, Athlete, Team, Set, Game_Info

class PlaySerializer(serializers.ModelSerializer):
    # Mostramos el nombre del atleta y el equipo en lugar de solo el ID
    athlete_name = serializers.ReadOnlyField(source='athlete.full_name')
    team_name = serializers.ReadOnlyField(source='team.name')

    class Meta:
        model = Play
        fields = [
            'id', 'action_type', 'sub_action', 'evaluation', 
            'athlete', 'athlete_name', 'team', 'team_name', 
            'set_period', 'timestamp', 'origin_zone', 
            'target_zone', 'wind'
        ]

    def validate_evaluation(self, value):
        """Validación personalizada: La escala debe ser 0-4"""
        if value < 0 or value > 4:
            raise serializers.ValidationError("La evaluación debe estar entre 0 y 4.")
        return value
    
class AthleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Athlete
        fields = ['id', 'full_name', 'sex']

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

from .models import Player

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
    category = serializers.CharField()
    subAction = serializers.CharField()
    playerId = serializers.CharField()
    value = serializers.IntegerField(required=False, allow_null=True)
    origin = serializers.CharField(required=False, allow_blank=True)
    destination = serializers.CharField(required=False, allow_blank=True)
    wind = serializers.CharField(required=False, allow_blank=True)
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