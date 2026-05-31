from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from datetime import timedelta

# 1. USUARIO (Acceso multiplataforma: Móvil/PC)
class User(AbstractUser):
    email = models.EmailField(unique=True)
    ROLE_CHOICES = (('admin', 'Administrador'), ('coach', 'Entrenador'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='coach')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Athlete(models.Model):
    SEX_CHOICES = [('M', 'Masculino'), ('F', 'Femenino')]
    full_name = models.CharField(max_length=100)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, default='M')

    def __str__(self):
        return self.full_name


class Player(models.Model):
    POSITION_CHOICES = [('B', 'Bloqueador'), ('D', 'Defensor'), ('U', 'Universal')]
    ZONE_CHOICES = [('IZQ', 'Izquierda'), ('CEN', 'Centro'), ('DER', 'Derecha')]

    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE, related_name='roles', null=True)
    number = models.IntegerField(default=1)
    position = models.CharField(max_length=1, choices=POSITION_CHOICES, default='B')
    zone = models.CharField(max_length=3, choices=ZONE_CHOICES, default='CEN')
    fullName = models.CharField(max_length=100, default='')

    def __str__(self):
        return f"{self.athlete.full_name} (#{self.number})" if self.athlete else f"#{self.number}"


class Team(models.Model):
    name = models.CharField(max_length=100, default='')
    players = models.ManyToManyField(Player, related_name='teams')

    def __str__(self):
        return self.name


# --- Captura de datos y Estado de Partido (REDISEÑADO) ---

class Game_Info(models.Model):
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'En Curso / Parcial'),
        ('COMPLETED', 'Finalizado / Oficial'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='IN_PROGRESS')

    # Equipos
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='game_team_a', verbose_name="Equipo A")
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='game_team_b', verbose_name="Equipo B")

    # Metadatos del partido (MatchConfig)
    tournament = models.CharField(max_length=200, default='')
    category = models.CharField(max_length=100, default='')
    date = models.CharField(max_length=30, default='')
    matchNumber = models.IntegerField(default=0)
    gender = models.CharField(max_length=1, default='M')
    eventType = models.CharField(max_length=50, default='')
    startTime = models.CharField(max_length=10, blank=True, null=True)
    place = models.CharField(max_length=100, blank=True, null=True)
    denomination = models.CharField(max_length=200, blank=True, null=True)
    meso = models.CharField(max_length=50, blank=True, null=True)
    micro = models.CharField(max_length=50, blank=True, null=True)
    weekDay = models.CharField(max_length=10, blank=True, null=True)
    microNumber = models.CharField(max_length=10, blank=True, null=True)
    objective = models.CharField(max_length=200, blank=True, null=True)
    platform = models.CharField(max_length=10, blank=True, null=True)
    createdBy = models.EmailField(blank=True, null=True)

    # Puntuación y tiempos
    pointsA = models.IntegerField(default=0)
    pointsB = models.IntegerField(default=0)
    setsA = models.IntegerField(default=0)
    setsB = models.IntegerField(default=0)
    currentSet = models.IntegerField(default=1)
    totalTimeSeconds = models.IntegerField(null=True, blank=True)
    realTimeSeconds = models.IntegerField(null=True, blank=True)

    # Datos finales
    final_score_a = models.IntegerField(default=0)
    final_score_b = models.IntegerField(default=0)
    total_duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.team_a} vs {self.team_b} ({self.status})"


class Set(models.Model):
    game = models.ForeignKey(Game_Info, on_delete=models.CASCADE, related_name='sets')
    set_number = models.IntegerField(default=1)
    time_set = models.DurationField(blank=True, null=True)
    score_a = models.IntegerField(default=0)
    score_b = models.IntegerField(default=0)
    set_winner = models.CharField(blank=True, null=True, max_length=100)


class Rally(models.Model):
    set = models.ForeignKey(Set, on_delete=models.CASCADE, related_name='rallies')
    winner = models.CharField(max_length=1, blank=True, null=True)   # 'A' o 'B'
    score_a = models.IntegerField(default=0)   # marcador al inicio del rally
    score_b = models.IntegerField(default=0)


class Play(models.Model):
    ACTION_CHOICES = [
        ('SERVICIO', 'Servicio'),
        ('RECEPCION', 'Recepción'),
        ('ACOMODADA', 'Acomodada'),
        ('ATAQUE', 'Ataque'),
        ('BLOQUEO', 'Bloqueo'),
        ('DEFENSA', 'Defensa'),
        ('ERRORES_SERV', 'Error de Servicio'),
        ('ERRORES_COM', 'Error de Comunicación'),
        ('ERRORES_POS', 'Error de Posicionamiento'),
        ('ERRORES_TEC', 'Error Técnico'),
    ]

    SUB_ACTION_CHOICES = [
        # Servicio
        ('BAJ', 'Por abajo'), ('FLO', 'Flotado'), ('SAL', 'Salto fuerte'), ('SAF', 'Salto flotado'),
        # Recepción
        ('2ma', 'Dos manos abajo'), ('Ppm', 'Pirámide/Puño'),
        # Acomodada
        ('P2a', 'Dos manos arriba'), ('P2b', 'Dos manos abajo'),
        # Ataque
        ('Rm', 'Remate fuerte'), ('Rca', 'Remate colocado'), ('Ub', 'Usa Bloqueo'),
        ('Tr', 'Tiro de nudillo'), ('Acd', 'Acomodada directa'), ('Rdjn', 'RDJN'),
        ('Rdpmp', 'RDPMP'), ('Rd', 'Recibo directo'),
        # Bloqueo
        ('Bl', 'Línea'), ('Bd', 'Diagonal'), ('Bn', 'No bloquea/Cubre'),
        # Defensa
        ('Dd', 'Diagonal desafiando'), ('Dltd', 'Hacia la línea'),
        ('Ld', 'Línea a diagonal'), ('Cc', 'Centro'),
        # Errores de servicio
        ('SFC', 'Saque fuera de cancha'), ('SR', 'Saque red'), ('SME', 'Saque mal ejecutado'),
        # Errores de comunicación
        ('CI', 'Confusión interna'), ('MC', 'Mala comunicación'),
        # Errores de posicionamiento
        ('NAT', 'No atento'), ('CJR', 'Caída en jugada rival'), ('MCA', 'Mala colocación anticipada'),
        ('JFZ', 'Jugador fuera de zona'),
        # Errores técnicos
        ('GMD', 'Golpe mal dirigido'), ('TI', 'Toque incorrecto'), ('MER', 'Mala ejecución de remate'),
        ('BTR', 'Bloqueo tras red'),
    ]

    WIND_CHOICES = [
        ('VIENTO A FAVOR', 'A favor'),
        ('VIENTO EN CONTRA', 'En contra'),
    ]

    action_type = models.CharField(max_length=30, choices=ACTION_CHOICES)
    sub_action = models.CharField(max_length=30, choices=SUB_ACTION_CHOICES, null=True, blank=True)
    evaluation = models.IntegerField(default=0, help_text="0=Negativo, 4=Positivo. Escala 0-4")

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='plays')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_plays')
    rally = models.ForeignKey(Rally, on_delete=models.CASCADE, related_name='plays')

    origin_zone = models.CharField(max_length=30, blank=True, null=True)
    target_zone = models.CharField(max_length=30, blank=True, null=True)
    timestamp = models.CharField(max_length=30, help_text="Formato MM:SS o ISO")
    wind = models.CharField(max_length=30, choices=WIND_CHOICES, blank=True, null=True)


# --- Clases padre (Abstractas) sin cambios ---

class Base_Event(models.Model):
    local_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    date = models.DateField()
    sex = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino')])
    category = models.CharField(max_length=50)
    game_data = models.OneToOneField('Game_Info', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        abstract = True

class Mix_Game(Base_Event):
    MESO_CHOICES = [
        ('ENT', 'Entrante'), ('BAS', 'Básico'), ('BDE', 'Básico desarrollador'),
        ('BES', 'Básico estabilizador'), ('PRE_CON', 'Preparatorio de control'),
        ('PRE_COM', 'Precompetitivo'), ('COM', 'Competitivo'),
        ('RES_MAN', 'De restablecimiento mantenedor'), ('PRE_RES', 'Preparatorio de restablecimiento'),
        ('PRE_MAN', 'Preparatorio de mantenimiento'),
    ]
    MICRO_CHOICES = [
        ('ORD', 'Ordinario'), ('CHO', 'De choque intensivo'),
        ('APR', 'De aproximación'), ('COM', 'Competitivo'),
        ('REC', 'De recuperación o restablecimiento'),
    ]
    WEEK_CHOICES = [
        ('LUN','Lunes'), ('MAR','Martes'),('MIE','Miércoles'), ('JUE','Jueves'),
        ('VIE','Viernes'), ('SAB','Sábado'), ('DOM','Domingo')
    ]
    meso_denomination = models.CharField(max_length=10, choices=MESO_CHOICES)
    micro_denomination = models.CharField(max_length=10, choices=MICRO_CHOICES)
    week_day = models.CharField(max_length=10, default='Lunes', choices=WEEK_CHOICES)
    micro_number = models.IntegerField(default=0)

    class Meta:
        abstract = True

class Mix_Game_Place(Mix_Game):
    place = models.CharField(max_length=100)

    class Meta:
        abstract = True

class Competition(Base_Event):
    denomination = models.CharField(max_length=100)
    place = models.CharField(max_length=100)
    start_time = models.TimeField()
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='competition_team_a', null=True, verbose_name="Equipo A")
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='competition_team_b', null=True, verbose_name="Equipo B")

class Intern_Control_Game(Mix_Game_Place):
    pass

class Training(Mix_Game):
    objective = models.CharField(max_length=200)

class Extern_Control_Game(Mix_Game_Place):
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='extern_team_a', null=True, verbose_name="Equipo A")
    team_b = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='extern_team_b', null=True, verbose_name="Equipo B")