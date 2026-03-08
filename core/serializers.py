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