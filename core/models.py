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
    # Denominación y lugar permitirán el "autocompletado" en el front buscando valores existentes
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

# --- Estructura de Atletas y Equipos (El Historial) ---

class Athlete(models.Model):
    """
    NÚCLEO DEL HISTORIAL: Aquí se guardan los datos fijos del deportista.
    Permite búsquedas por nombre y es la base para el 'Diagrama de Araña'.
    """
    full_name = models.CharField(max_length=100, unique=True)
    sex = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino')])
    
    def __str__(self):
        return self.full_name

class Player(models.Model):
    """
    EL ROL: El Atleta jugando un partido específico con un número y posición.
    """
    # El Player apunta al Atleta para mantener la conexión con su historial global
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='roles', null=True)
    number = models.IntegerField(default=1)
    position = models.CharField(max_length=50) 
    zone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.athlete.full_name} (#{self.number})"

class Team(models.Model):
    """
    EQUIPOS: Permite buscar estadísticas grupales.
    """
    name = models.CharField(max_length=100, unique=True)
    # player1 y player2 vinculados a sus roles de Player
    player1 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='team_p1', null=True)
    player2 = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='team_p2', null=True)

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
    """
    CONTROL DE ESTADOS: Permite diferenciar entre 'Visualizar Resultados' 
    (finalizado) y 'Cargar Partido' (en curso).
    """
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'En Curso / Parcial'),
        ('COMPLETED', 'Finalizado / Oficial'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='IN_PROGRESS')
    
    team_1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='game_team_1')
    team_2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='game_team_2')
    
    # Datos finales para el informe de 'Visualizar Resultados'
    final_score_t1 = models.IntegerField(default=0)
    final_score_t2 = models.IntegerField(default=0)
    total_duration = models.DurationField(null=True, blank=True)

    # Relación con los sets
    set_1 = models.ForeignKey(Set, on_delete=models.CASCADE, related_name='game_set_1', null=True)
    set_2 = models.ForeignKey(Set, on_delete=models.CASCADE, related_name='game_set_2', null=True)
    set_3 = models.ForeignKey(Set, on_delete=models.CASCADE, related_name='game_set_3', null=True, blank=True)

class Play(models.Model):
    """
    ESTADÍSTICA PURA: Cada acción alimenta el historial del ATLETA.
    """
    ACTION_CHOICES = [
        ('SER', 'Servicio'), ('REC', 'Recepción'), ('ACO', 'Acomodada'),
        ('ATA', 'Ataque'), ('BLO', 'Bloqueo'), ('DEF', 'Defensa'),
        ('ENF', 'Error No Forzado')
    ]
    action_type = models.CharField(max_length=3, choices=ACTION_CHOICES)

    # SUB-ACCIONES (Solo PC)
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

    # EVALUACIÓN (0 a 4): Base para el diagrama de araña
    evaluation = models.IntegerField(default=0)

    # VINCULACIÓN: La jugada pertenece a un Atleta (historial) y a un partido (contexto)
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='performances', null=True)
    game_info = models.ForeignKey(Game_Info, on_delete=models.CASCADE, related_name='plays', null=True)
    set_period = models.ForeignKey(Set, on_delete=models.CASCADE, related_name='plays')
    
    timestamp = models.CharField(max_length=10) # Formato MM:SS para el cronómetro
    origin_zone = models.CharField(max_length=10, null=True, blank=True)
    target_zone = models.CharField(max_length=10, null=True, blank=True)
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