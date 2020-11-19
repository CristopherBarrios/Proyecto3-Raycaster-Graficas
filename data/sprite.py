#Cristopher Jose Rodolfo Barrios Solis
#18207
from data.raycaster import mapping
from collections import deque
from numba.typed import Dict
from numba.core import types
from data.configuracion import *
from numba import int32
import pygame

class Sprite:
    def __init__(self, params, position):
        self.object = params["sprite"].copy()
        self.viewing_angles = params["angulos"]
        self.shift = params["cambio"]
        self.scale = params["escala"]
        self.animation = params["animacion"].copy()
        self.death_animation = params["animaMuerte"].copy()
        self.is_dead = params["muerto"]
        self.dead_shift = params["cambioMuerte"]
        self.animation_dist = params["dist"]
        self.animation_speed = params["speed"]
        self.blocked = params["bloqueado"]
        self.flag = params["bandera"]
        self.obj_action = params["accion"].copy()
        self.x, self.y = position[0] * TILE, position[1] * TILE
        self.side = params["sitio"]
        self.dead_animation_count = 0
        self.animation_count = 0
        self.enemy_action_trigger = False
        self.door_open_trigger = False
        self.door_prev_position = self.y if self.flag == "hori" else self.x
        self.delete = False
        if self.viewing_angles:
            if len(self.object) == 8:
                self.sprite_angles = [
                    frozenset(range(338, 361)) | frozenset(range(0, 23))
                ] + [frozenset(range(i, i + 45)) for i in range(23, 338, 45)]
            else:
                self.sprite_angles = [
                    frozenset(range(348, 361)) | frozenset(range(0, 11))
                ] + [frozenset(range(i, i + 23)) for i in range(11, 348, 23)]
            self.sprite_positions = {
                angle: position
                for angle, position in zip(self.sprite_angles, self.object)
            }
    @property
    def position(self):
        return self.x - self.side // 2, self.y - self.side // 2
    def enemy_in_action(self):
        sprite_object = self.obj_action[0]
        if self.animation_count < self.animation_speed:
            self.animation_count += 1
        else:
            self.obj_action.rotate()
            self.animation_count = 0
        return sprite_object
    def door_open(self):
        if self.flag == "hori":
            self.y -= 3
            if abs(self.y - self.door_prev_position) > TILE:
                self.delete = True
        elif self.flag == "verti":
            self.x -= 3
            if abs(self.x - self.door_prev_position) > TILE:
                self.delete = True
    def object_locate(self, player):
        dx, dy = self.x - player.x, self.y - player.y
        self.distance_to_sprite = math.sqrt(dx ** 2 + dy ** 2)
        self.theta = math.atan2(dy, dx)
        gamma = self.theta - player.angle
        if dx > 0 and 180 <= math.degrees(player.angle) <= 360 or dx < 0 and dy < 0:
            gamma += 2 * math.pi
        self.theta -= 1.4 * gamma
        delta_rays = int(gamma / DELTA_ANGLE)
        self.current_ray = CENTER_RAY + delta_rays
        if self.flag not in {"hori", "verti"}:
            self.distance_to_sprite *= math.cos(
                HALF_FOV - self.current_ray * DELTA_ANGLE
            )
        fake_ray = self.current_ray + FAKE_RAYS
        if 0 <= fake_ray <= FAKE_RAYS_RANGE and self.distance_to_sprite > 30:
            self.projection_height = min(
                int(PROJECTION_COEFFICIENT / self.distance_to_sprite),
                DOUBLE_HEIGHT if self.flag not in {"hori", "verti"} else HEIGHT,
            )
            sprite_width = int(self.projection_height * self.scale[0])
            sprite_height = int(self.projection_height * self.scale[1])
            half_sprite_width = sprite_width // 2
            half_sprite_height = sprite_height // 2
            shift = half_sprite_height * self.shift
            if self.flag == "hori" or self.flag == "verti":
                if self.door_open_trigger:
                    self.door_open()
                self.object = self.visible_sprite()
                sprite_object = self.sprite_animation()
            else:
                if self.is_dead and self.is_dead != "immortal":
                    sprite_object = self.dead_animation()
                    shift = half_sprite_height * self.dead_shift
                    sprite_height = int(sprite_height / 1.3)
                elif self.enemy_action_trigger:
                    sprite_object = self.enemy_in_action()
                else:
                    self.object = self.visible_sprite()
                    sprite_object = self.sprite_animation()
            sprite = pygame.transform.scale(
                sprite_object, (sprite_width, sprite_height)
            )
            sprite_position = (
                self.current_ray * SCALE - half_sprite_width,
                HALF_HEIGHT - half_sprite_height + shift,
            )
            return (self.distance_to_sprite, sprite, sprite_position)
        else:
            return (False,)
    def dead_animation(self):
        if len(self.death_animation):
            if self.dead_animation_count < self.animation_speed:
                self.dead_sprite = self.death_animation[0]
                self.dead_animation_count += 1
            else:
                self.dead_sprite = self.death_animation.popleft()
                self.dead_animation_count = 0
        return self.dead_sprite
    @property
    def is_on_fire(self):
        if (
            CENTER_RAY - self.side // 2 < self.current_ray < CENTER_RAY + self.side // 2
            and self.blocked
        ):
            return (self.distance_to_sprite, self.projection_height)
        return (float("inf"), None)
    def sprite_animation(self):
        if self.animation and self.distance_to_sprite < self.animation_dist:
            sprite_object = self.animation[0]
            if self.animation_count < self.animation_speed:
                self.animation_count += 1
            else:
                self.animation.rotate(-1)
                self.animation_count = 0
            return sprite_object
        return self.object
    def visible_sprite(self):
        if self.viewing_angles:
            if self.theta < 0:
                self.theta += 2 * math.pi
            self.theta = 360 - int(math.degrees(self.theta))
            for angles in self.sprite_angles:
                if self.theta in angles:
                    return self.sprite_positions[angles]
        return self.object
class Spritaton:
    def __init__(self):
        self.sprite_params = {
            "MesaCrafteo": {
                "sprite": pygame.image.load(
                    "./data/sprites/crafteo/base/0.png"
                ).convert_alpha(),
                "angulos": None,
                "cambio": 1.8,
                "escala": (0.4, 0.4),
                "sitio": 30,
                "animacion": deque(
                    [
                        pygame.image.load(
                            f"./data/sprites/crafteo/anim/{i}.png"
                        ).convert_alpha()
                        for i in range(12)
                    ]
                ),
                "animaMuerte": deque(
                    [
                        pygame.image.load(
                            f"./data/sprites/crafteo/death/{i}.png"
                        ).convert_alpha()
                        for i in range(4)
                    ]
                ),
                "muerto": None,
                "cambioMuerte": 2.6,
                "dist": 800,
                "speed": 6,
                "bloqueado": True,
                "bandera": "decor",
                "accion": [],
            },
            "chucho": {
                "sprite": pygame.image.load(
                    "./data/sprites/chucho/base/0.png"
                ).convert_alpha(),
                "angulos": None,
                "cambio": 0.6,
                "escala": (0.6, 0.6),
                "sitio": 30,
                "animacion": deque(
                    [
                        pygame.image.load(
                            f"./data/sprites/chucho/anim/{i}.png"
                        ).convert_alpha()
                        for i in range(8)
                    ]
                ),
                "animaMuerte": [],
                "muerto": "immortal",
                "cambioMuerte": None,
                "dist": 800,
                "speed": 10,
                "bloqueado": True,
                "bandera": "decor",
                "accion": [],
            },
            "pasto": {
                "sprite": pygame.image.load(
                    "./data/sprites/pasto/base/0.png"
                ).convert_alpha(),
                "angulos": None,
                "cambio": 0.7,
                "escala": (0.6, 0.6),
                "sitio": 30,
                "animacion": deque(
                    [
                        pygame.image.load(
                            f"./data/sprites/pasto/anim/{i}.png"
                        ).convert_alpha()
                        for i in range(16)
                    ]
                ),
                "animaMuerte": [],
                "muerto": "immortal",
                "cambioMuerte": 1.8,
                "dist": 1800,
                "speed": 5,
                "bloqueado": None,
                "bandera": "decor",
                "accion": [],
            },
            "zomby": {
                "sprite": [
                    pygame.image.load(
                        f"./data/sprites/mobs/zomboy/base/{i}.png"
                    ).convert_alpha()
                    for i in range(8)
                ],
                "angulos": True,
                "cambio": 0.0,
                "escala": (1.1, 1.1),
                "sitio": 50,
                "animacion": [],
                "animaMuerte": deque(
                    [
                        pygame.image.load(
                            f"./data/sprites/mobs/zomboy/death/{i}.png"
                        ).convert_alpha()
                        for i in range(6)
                    ]
                ),
                "muerto": None,
                "cambioMuerte": 0.6,
                "dist": None,
                "speed": 10,
                "bloqueado": True,
                "bandera": "mobs",
                "accion": deque(
                    [
                        pygame.image.load(
                            f"./data/sprites/mobs/zomboy/anim/{i}.png"
                        ).convert_alpha()
                        for i in range(9)
                    ]
                ),
            },
            "murcielago": {
                "sprite": [
                    pygame.image.load(
                        f"./data/sprites/mobs/murcielago/base/{i}.png"
                    ).convert_alpha()
                    for i in range(8)
                ],
                "angulos": True,
                "cambio": 0,
                "escala": (0.9, 1.0),
                "sitio": 30,
                "animacion": [],
                "animaMuerte": deque(
                    [
                        pygame.image.load(
                            f"./data/sprites/mobs/murcielago/death/{i}.png"
                        ).convert_alpha()
                        for i in range(11)
                    ]
                ),
                "muerto": None,
                "cambioMuerte": 0.5,
                "dist": None,
                "speed": 6,
                "bloqueado": True,
                "bandera": "mobs",
                "accion": deque(
                    [
                        pygame.image.load(
                            f"./data/sprites/mobs/murcielago/action/{i}.png"
                        ).convert_alpha()
                        for i in range(6)
                    ]
                ),
            },
            "gusanito": {
                "sprite": [
                    pygame.image.load(
                        f"./data/sprites/mobs/gusano/base/{i}.png"
                    ).convert_alpha()
                    for i in range(8)
                ],
                "angulos": True,
                "cambio": 0.8,
                "escala": (0.4, 0.6),
                "sitio": 30,
                "animacion": [],
                "animaMuerte": deque(
                    [
                        pygame.image.load(
                            f"./data/sprites/mobs/gusano/death/{i}.png"
                        ).convert_alpha()
                        for i in range(10)
                    ]
                ),
                "muerto": None,
                "cambioMuerte": 1.7,
                "dist": None,
                "speed": 6,
                "bloqueado": True,
                "bandera": "mobs",
                "accion": deque(
                    [
                        pygame.image.load(
                            f"./data/sprites/mobs/gusano/action/{i}.png"
                        ).convert_alpha()
                        for i in range(4)
                    ]
                ),
            },
            "creeper": {
                "sprite": [
                    pygame.image.load(
                        f"./data/sprites/mobs/creeper/base/{i}.png"
                    ).convert_alpha()
                    for i in range(8)
                ],
                "angulos": True,
                "cambio": 0.8,
                "escala": (0.4, 0.6),
                "sitio": 30,
                "animacion": [],
                "animaMuerte": deque(
                    [
                        pygame.image.load(
                            f"./data/sprites/mobs/creeper/death/{i}.png"
                        ).convert_alpha()
                        for i in range(11)
                    ]
                ),
                "muerto": None,
                "cambioMuerte": 1.7,
                "dist": None,
                "speed": 6,
                "bloqueado": True,
                "bandera": "mobs",
                "accion": deque(
                    [
                        pygame.image.load(
                            f"./data/sprites/mobs/creeper/action/{i}.png"
                        ).convert_alpha()
                        for i in range(4)
                    ]
                ),
            },
            "vertical": {
                "sprite": [
                    pygame.image.load(
                        f"./data/sprites/ladrillos/verti/{i}.png"
                    ).convert_alpha()
                    for i in range(16)
                ],
                "angulos": True,
                "cambio": 0.1,
                "escala": (2.6, 1.2),
                "sitio": 100,
                "animacion": [],
                "animaMuerte": [],
                "muerto": "immortal",
                "cambioMuerte": 0,
                "dist": 0,
                "speed": 0,
                "bloqueado": True,
                "bandera": "hori",
                "accion": [],
            },
            "horizontal": {
                "sprite": [
                    pygame.image.load(
                        f"./data/sprites/ladrillos/hori/{i}.png"
                    ).convert_alpha()
                    for i in range(16)
                ],
                "angulos": True,
                "cambio": 0.1,
                "escala": (2.6, 1.2),
                "sitio": 100,
                "animacion": [],
                "animaMuerte": [],
                "muerto": "immortal",
                "cambioMuerte": 0,
                "dist": 0,
                "speed": 0,
                "bloqueado": True,
                "bandera": "verti",
                "accion": [],
            },
        }
        self.list_of_objects = [
            Sprite(self.sprite_params["chucho"], (6.8, 3.2)),##chucho
            Sprite(self.sprite_params["chucho"], (4.8, 3.8)),
            Sprite(self.sprite_params["chucho"], (1.5, 1.5)),
            Sprite(self.sprite_params["chucho"], (1.2, 5.2)),
            Sprite(self.sprite_params["chucho"], (1.2, 11.5)),
            Sprite(self.sprite_params["chucho"], (12.5, 6.5)),
            Sprite(self.sprite_params["chucho"], (15.5, 10.5)),
            Sprite(self.sprite_params["chucho"], (19.5, 14.5)),
            Sprite(self.sprite_params["chucho"], (22.5, 12.5)),
            Sprite(self.sprite_params["chucho"], (23.8, 6.5)),
            Sprite(self.sprite_params["chucho"], (17.8, 1.5)),
            Sprite(self.sprite_params["creeper"], (5.5, 3.5)),##creeper
            Sprite(self.sprite_params["creeper"], (10.5, 5.5)),
            Sprite(self.sprite_params["creeper"], (3.5, 1.5)),
            Sprite(self.sprite_params["creeper"], (4.5, 5.5)),
            Sprite(self.sprite_params["creeper"], (3.5, 9.5)),
            Sprite(self.sprite_params["creeper"], (8.5, 12.5)),
            Sprite(self.sprite_params["creeper"], (12.5, 10.5)),
            Sprite(self.sprite_params["creeper"], (22.5, 7.5)),
            Sprite(self.sprite_params["creeper"], (17.5, 7.5)),
            Sprite(self.sprite_params["creeper"], (22.76, 10.21)),
            Sprite(self.sprite_params["gusanito"], (12.5, 1.5)),##gusanito
            Sprite(self.sprite_params["gusanito"], (15.5, 7.5)),
            Sprite(self.sprite_params["gusanito"], (9.5, 1.5)),
            Sprite(self.sprite_params["gusanito"], (1.5, 8.5)),
            Sprite(self.sprite_params["gusanito"], (8.5, 14.5)),
            Sprite(self.sprite_params["gusanito"], (19.5, 13.5)),
            Sprite(self.sprite_params["gusanito"], (22.5, 3.5)),
            Sprite(self.sprite_params["gusanito"], (22.5, 9.5)),
            Sprite(self.sprite_params["gusanito"], (17.5, 3.5)),
            Sprite(self.sprite_params["gusanito"], (17.5, 9.5)),
            Sprite(self.sprite_params["gusanito"], (2.5, 1.5)),
            Sprite(self.sprite_params["murcielago"], (14.5, 4.5)),## murcielago
            Sprite(self.sprite_params["murcielago"], (12.5, 8.5)),
            Sprite(self.sprite_params["murcielago"], (7.5, 7.5)),
            Sprite(self.sprite_params["murcielago"], (2.5, 11.5)),
            Sprite(self.sprite_params["murcielago"], (12.5, 14.5)),
            Sprite(self.sprite_params["murcielago"], (12.5, 12.5)),
            Sprite(self.sprite_params["murcielago"], (22.5, 5.5)),
            Sprite(self.sprite_params["murcielago"], (22.5, 11.5)),
            Sprite(self.sprite_params["murcielago"], (17.5, 5.5)),
            Sprite(self.sprite_params["murcielago"], (17.5, 11.5)),
            Sprite(self.sprite_params["zomby"], (3.5, 7.5)),## zombie
            Sprite(self.sprite_params["zomby"], (4.5, 13.5)),
            Sprite(self.sprite_params["zomby"], (17.5, 13.5)),
            Sprite(self.sprite_params["zomby"], (19.5, 3.5)),
            Sprite(self.sprite_params["zomby"], (19.5, 5.5)),
            Sprite(self.sprite_params["zomby"], (19.5, 7.5)),
            Sprite(self.sprite_params["zomby"], (19.5, 9.5)),
            Sprite(self.sprite_params["pasto"], (4.5, 1.5)),###cesped
            Sprite(self.sprite_params["pasto"], (8.5, 1.5)),
            Sprite(self.sprite_params["pasto"], (14.5, 4.5)),
            Sprite(self.sprite_params["pasto"], (15.5, 6.5)),
            Sprite(self.sprite_params["pasto"], (9.5, 10.5)),
            Sprite(self.sprite_params["pasto"], (7.5, 6.5)),
            Sprite(self.sprite_params["pasto"], (4.5, 5.5)),
            Sprite(self.sprite_params["pasto"], (3.5, 8.5)),
            Sprite(self.sprite_params["pasto"], (3.5, 8.5)),
            Sprite(self.sprite_params["pasto"], (1.5, 8.5)),
            Sprite(self.sprite_params["pasto"], (7.5, 8.5)),
            Sprite(self.sprite_params["pasto"], (3.5, 11.5)),
            Sprite(self.sprite_params["pasto"], (1.5, 13.5)),
            Sprite(self.sprite_params["pasto"], (1.5, 11.5)),
            Sprite(self.sprite_params["pasto"], (11.5, 14.5)),
            Sprite(self.sprite_params["pasto"], (11.5, 12.5)),
            Sprite(self.sprite_params["pasto"], (21.5, 11.5)),
            Sprite(self.sprite_params["pasto"], (21.5, 3.5)),
            Sprite(self.sprite_params["pasto"], (21.5, 6.5)),
            Sprite(self.sprite_params["pasto"], (22.5, 9.5)),
            Sprite(self.sprite_params["pasto"], (22.5, 12.5)),
            Sprite(self.sprite_params["pasto"], (22.5, 14.5)),
            Sprite(self.sprite_params["pasto"], (17.5, 3.5)),
            Sprite(self.sprite_params["pasto"], (17.5, 6.5)),
            Sprite(self.sprite_params["pasto"], (17.5, 9.5)),
            Sprite(self.sprite_params["pasto"], (17.5, 12.5)),
            Sprite(self.sprite_params["MesaCrafteo"], (7.5, 1.5)),##mesadeCrafteo
            Sprite(self.sprite_params["MesaCrafteo"], (5.5, 3.5)),
            Sprite(self.sprite_params["MesaCrafteo"], (10.5, 5.5)),
            Sprite(self.sprite_params["MesaCrafteo"], (3.5, 9.5)),
            Sprite(self.sprite_params["MesaCrafteo"], (2.5, 14.5)),
            Sprite(self.sprite_params["MesaCrafteo"], (10.5, 14.5)),
            Sprite(self.sprite_params["MesaCrafteo"], (22.5, 14.5)),
            Sprite(self.sprite_params["MesaCrafteo"], (22.5, 1.5)),
            Sprite(self.sprite_params["MesaCrafteo"], (15.5, 1.5)),
            Sprite(self.sprite_params["MesaCrafteo"], (13.5, 10.5)),
            Sprite(self.sprite_params["MesaCrafteo"], (7.5, 5.5)),
            Sprite(self.sprite_params["vertical"], (9.5, 1.5)),###puertitas verticales
            Sprite(self.sprite_params["vertical"], (9.5, 3.5)),
            Sprite(self.sprite_params["vertical"], (18.5, 3.5)),
            Sprite(self.sprite_params["vertical"], (18.5, 5.5)),
            Sprite(self.sprite_params["vertical"], (18.5, 7.5)),
            Sprite(self.sprite_params["vertical"], (18.5, 9.5)),
            Sprite(self.sprite_params["vertical"], (18.5, 11.5)),
            Sprite(self.sprite_params["vertical"], (7.5, 10.5)),
            Sprite(self.sprite_params["vertical"], (20.5, 5.5)),
            Sprite(self.sprite_params["vertical"], (20.5, 7.5)),
            Sprite(self.sprite_params["vertical"], (21.5, 9.5)),
            Sprite(self.sprite_params["horizontal"], (10.5, 2.5)),## puertitas horizontales
            Sprite(self.sprite_params["horizontal"], (12.5, 2.5)),
            Sprite(self.sprite_params["horizontal"], (3.5, 6.5)),
            Sprite(self.sprite_params["horizontal"], (3.5, 10.5)),
            Sprite(self.sprite_params["horizontal"], (4.5, 12.5)),
            Sprite(self.sprite_params["horizontal"], (17.5, 12.5)),
            Sprite(self.sprite_params["horizontal"], (10.5, 13.5)),
            Sprite(self.sprite_params["horizontal"], (19.5, 12.5)),
        ]
    @property
    def sprite_shot(self):
        return min(
            [obj.is_on_fire for obj in self.list_of_objects], default=(float("inf"), 0)
        )
    @property
    def blocked_doors(self):
        blocked_doors = Dict.empty(key_type=types.UniTuple(int32, 2), value_type=int32)
        for obj in self.list_of_objects:
            if obj.flag == "hori" or obj.flag == "verti":
                if obj.blocked:
                    i, j = mapping(obj.x, obj.y)
                    blocked_doors[(i, j)] = 0
        return blocked_doors
