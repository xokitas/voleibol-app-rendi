from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    User, Athlete, Player, Team, Set, Play, 
    Game_Info, Competition, Intern_Control_Game, 
    Training, Extern_Control_Game
)

# Registramos todos los modelos para poder gestionarlos desde la web
admin.site.register(User)
admin.site.register(Athlete)
admin.site.register(Player)
admin.site.register(Team)
admin.site.register(Set)
admin.site.register(Play)
admin.site.register(Game_Info)
admin.site.register(Competition)
admin.site.register(Intern_Control_Game)
admin.site.register(Training)
admin.site.register(Extern_Control_Game)