#Cristopher Jose Rodolfo Barrios Solis
#18207
from data.raycaster import ray_casting_walls
from data.jugador import JUUGADOR
from data.logica import Logc
from data.sprite import *
from data.ui import UI

pygame.init()
pantalla = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)
reloj = pygame.time.Clock()
MapaBase = pygame.Surface(MAP_RESOLUTION)
sprt = Spritaton()
jugador = JUUGADOR(sprt)
ui = UI(pantalla, MapaBase, jugador, reloj)
lg = Logc(jugador, sprt, ui)
ui.principal()
pygame.mouse.set_visible(False)
ui.musiquita()

while True:
    jugador.movement()
    ui.fondo()
    walls, wall_shot = ray_casting_walls(jugador, ui.textures)
    ui.mundo(walls + [obj.object_locate(jugador) for obj in sprt.list_of_objects])
    ui.fps(reloj)
    ui.mapita()
    ui.arma([wall_shot, sprt.sprite_shot])
    lg.objetos()
    lg.mobs()
    lg.aclarar()
    lg.SeraqueGano()
    pygame.display.flip()
    reloj.tick()
