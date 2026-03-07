from django.contrib import admin
from .models import (
    User, Athlete, Player, Team, Set, Play, 
    Game_Info, Competition, Intern_Control_Game, 
    Training, Extern_Control_Game
)

# --- CONFIGURACIÓN DE EVENTOS CON DIVISIONES LÓGICAS ---

@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Información General', {
            'fields': ('denomination', 'date', 'place', 'sex', 'category', 'start_time')
        }),
        ('Equipos que se enfrentan', {
            'fields': (('team_a', 'team_b'),)
        }),
        ('Estadísticas', {
            'fields': ('game_data',)
        }),
    )

@admin.register(Extern_Control_Game)
class ExternAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Información General', {
            'fields': ('date', 'place', 'sex', 'category', 'meso_denomination', 'micro_denomination', 'week_day', 'micro_number')
        }),
        ('Equipos que se enfrentan', {
            'fields': (('team_a', 'team_b'),)
        }),
        ('Estadísticas', {
            'fields': ('game_data',)
        }),
    )

@admin.register(Intern_Control_Game)
class InternAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Información General', {
            'fields': ('meso_denomination', 'micro_denomination', 'date', 'week_day', 'micro_number', 'place', 'sex', 'category')
        }),
        ('Estadísticas', {
            'fields': ('game_data',)
        }),
    )

@admin.register(Training)
class TrainingAdmin(admin.ModelAdmin):
    # Aplicando exactamente los campos de tu versión corregida
    fieldsets = (
        ('Información General', {
            'fields': ('meso_denomination', 'micro_denomination', 'date', 'week_day', 'micro_number', 'sex', 'category', 'objective')
        }),
        ('Estadísticas', {
            'fields': ('game_data',)
        }),
    )

# --- REGISTROS DE MODELOS DE SOPORTE ---

admin.site.register(User)
admin.site.register(Athlete)
admin.site.register(Player)
admin.site.register(Team)
admin.site.register(Set)
admin.site.register(Play)
admin.site.register(Game_Info)