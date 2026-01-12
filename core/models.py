from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# 1. USUARIO (Acceso multiplataforma: Móvil/PC)
class User(AbstractUser):
    ROLE_CHOICES = (('admin', 'Administrador'), ('coach', 'Entrenador'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='coach')

# --- Clases padre (Abstractas) para organizar los eventos ---

class Base_Event(models.Model):
    # local_uuid: Vital para que el móvil cree eventos sin internet y no choquen con la PC
    local_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False) 
    # Denominación y lugar permitirán el "autocompletado" buscando valores existentes
    denomination = models.CharField(max_length=100) 
    date = models.DateField()
    sex = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino')])
    category = models.CharField(max_length=50)

    class Meta:
        abstract = True

class Mix_Game(Base_Event):
    micro_denomination = models.CharField(max_length=150, default='')
    week_day = models.CharField(max_length=10, default='Lunes') 
    micro_number = models.IntegerField(default=0)

    class Meta:
        abstract = True 

class Mix_Game_Place(Mix_Game):
    place = models.CharField(max_length=100)

    class Meta:
        abstract = True 

# --- Estructura de Atletas y Equipos (Historial y Roster) ---

class Athlete(models.Model):
    """
    NÚCLEO DEL HISTORIAL: Aquí se guardan los datos fijos del deportista.
    """
    full_name = models.CharField(max_length=100, unique=True)
    sex = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino')])
    
    def __str__(self):
        return self.full_name

class Player(models.Model):
    """
    EL ROL: El Atleta jugando con un número y posición específica.
    """
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='roles', null=True)
    number = models.IntegerField(default=1)
    position = models.CharField(max_length=50) 
    zone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.athlete.full_name} (#{self.number})"

class Team(models.Model):
    name = models.CharField(max_length=100, default='')
    
    # CAMBIO IMPORTANTE: ManyToManyField
    # Permite registrar 2 jugadores (Competencia) o N jugadores (Entrenamiento).
    # Esto soluciona la rotación de jugadores en el entrenamiento.
    players = models.ManyToManyField(Player, related_name='teams')

    def __str__(self):
        return self.name

# --- Captura de datos y Estado de Partido ---

class Set(models.Model):
    set_number = models.IntegerField(default=1) # 1, 2 o 3
    time_set = models.DurationField(blank=True, null=True)
    score_a = models.IntegerField(default=0)
    score_b = models.IntegerField(default=0)
    set_winner = models.CharField(blank=True, null=True, max_length=100)

class Game_Info(models.Model):
    # Estados para diferenciar 'Cargar Partido' vs 'Visualizar Resultados'
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'En Curso / Parcial'),
        ('COMPLETED', 'Finalizado / Oficial'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='IN_PROGRESS')

    team_1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='game_team_1')
    team_2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='game_team_2')
    
    # Datos finales
    final_score_t1 = models.IntegerField(default=0)
    final_score_t2 = models.IntegerField(default=0)
    total_duration = models.DurationField(null=True, blank=True)
    
    # Relación con los sets
    set_1 = models.ForeignKey(Set, on_delete=models.CASCADE, related_name='game_set_1', null=True)
    set_2 = models.ForeignKey(Set, on_delete=models.CASCADE, related_name='game_set_2', null=True)
    set_3 = models.ForeignKey(Set, on_delete=models.CASCADE, related_name='game_set_3', null=True, blank=True)

class Play(models.Model):
    """
    Esta tabla unifica la captura de Móvil y PC.
    El móvil enviará solo lo básico. La PC enviará los campos null=True.
    """
    # ACCIONES (Las 6 básicas + Error No Forzado del Guion)
    ACTION_CHOICES = [
        ('SER', 'Servicio'), ('REC', 'Recepción'), ('ACO', 'Acomodada'),
        ('ATA', 'Ataque'), ('BLO', 'Bloqueo'), ('DEF', 'Defensa'),
        ('ENF', 'Error No Forzado')
    ]
    action_type = models.CharField(max_length=3, choices=ACTION_CHOICES)

    # SUB-ACCIONES (Solo PC - Se quedan en blanco si vienen del móvil)
    SUB_ACTION_CHOICES = [
        ('BAJ', 'Por abajo'), ('FLO', 'Flotado'), ('SAL', 'Salto fuerte'), ('SAF', 'Salto flotado'), 
        ('2MA', 'Dos manos abajo'), ('PPM', 'Pirámide/Puño'), 
        ('P2A', 'Dos manos arriba'), ('P2B', 'Dos manos abajo'), 
        ('RM', 'Remate fuerte'), ('RCA', 'Remate colocado'), ('UB', 'Usa Bloqueo'), 
        ('TR', 'Tiro de nudillo'), ('ADC', 'Acomodada directa'), ('RD', 'Recibo directo'),
        ('BL', 'Línea'), ('BD', 'Diagonal'), ('BN', 'No bloquea/Cubre'), 
        ('DD', 'Diagonal desafiando'), ('DLT', 'Hacia la línea'), ('LD', 'Línea a diagonal'), ('CC', 'Centro')
    ]
    sub_action = models.CharField(max_length=3, choices=SUB_ACTION_CHOICES, null=True, blank=True)

    # NUEVA EVALUACIÓN (0 a 4)
    evaluation = models.IntegerField(default=0, help_text="0=Negativo, 4=Positivo. Escala 0-4")

    # VINCULACIÓN:
    # Vinculamos directo al Atleta para mantener estadísticas aunque se cambie de equipo o rol
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='performances', null=True)
    # Vinculamos al Team para saber a qué bando pertenecía el punto en ese momento
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_plays', null=True)
    
    set_period = models.ForeignKey(Set, on_delete=models.CASCADE, related_name='plays')
    timestamp = models.CharField(max_length=10, help_text="Formato MM:SS") 

    # ZONAS (Solo PC)
    origin_zone = models.CharField(max_length=10, null=True, blank=True)
    target_zone = models.CharField(max_length=10, null=True, blank=True)

    # VIENTO (Mencionado en el Guion como factor externo)
    wind = models.CharField(max_length=1, choices=[('F', 'A favor'), ('C', 'En contra')], null=True, blank=True)

# --- Clases Hijas: Los 4 Tipos de Eventos Reales ---

class Competition(Base_Event):
    place = models.CharField(max_length=100) 
    start_time = models.TimeField()
    game_data = models.OneToOneField(Game_Info, on_delete=models.CASCADE, null=True)

class Intern_Control_Game(Mix_Game_Place):
    game_data = models.OneToOneField(Game_Info, on_delete=models.CASCADE, null=True)

class Training(Base_Event):
    objective = models.CharField(max_length=200)
    game_data = models.OneToOneField(Game_Info, on_delete=models.CASCADE, null=True)

class Extern_Control_Game(Mix_Game_Place):
    rival_team_name = models.CharField(max_length=150)
    game_data = models.OneToOneField(Game_Info, on_delete=models.CASCADE, null=True)