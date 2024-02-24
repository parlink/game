from settings import VERTICAL_TILE_NUMBER, TILE_SIZE, SCREEN_WIDTH
import pygame
from tiles import AnimatedTile, StaticTile
from utils import import_folder
from random import choices, randint


class Sky:
    def __init__(self, horizon, style="level"):
        self.top = pygame.image.load("../graphics/decoration/sky/sky_top.png").convert()
        self.bottom = pygame.image.load(
            "../graphics/decoration/sky/sky_bottom.png"
        ).convert()
        self.middle = pygame.image.load(
            "../graphics/decoration/sky/sky_middle.png"
        ).convert()
        self.horizon = horizon

        # stretch
        self.top = pygame.transform.scale(self.top, (SCREEN_WIDTH, TILE_SIZE))
        self.bottom = pygame.transform.scale(self.bottom, (SCREEN_WIDTH, TILE_SIZE))
        self.middle = pygame.transform.scale(self.middle, (SCREEN_WIDTH, TILE_SIZE))

        self.style = style
        if self.style == "overworld":
            palm_surfaces = import_folder("../graphics/overworld/palms")
            self.palms = []

            for surface in choices(palm_surfaces, k=10):
                x = randint(0, SCREEN_WIDTH)
                y = (self.horizon * TILE_SIZE) + randint(50, 100)
                rect = surface.get_rect(midbottom=(x, y))
                self.palms.append((surface, rect))

            cloud_surfaces = import_folder("../graphics/overworld/clouds")
            self.clouds = []

            for surface in choices(cloud_surfaces, k=10):
                x = randint(0, SCREEN_WIDTH)
                y = randint(0, (self.horizon * TILE_SIZE) - 100)
                rect = surface.get_rect(midbottom=(x, y))
                self.clouds.append((surface, rect))

    def draw(self, surface):
        for row in range(VERTICAL_TILE_NUMBER):
            y = row * TILE_SIZE
            if row < self.horizon:
                surface.blit(self.top, (0, y))
            elif row == self.horizon:
                surface.blit(self.middle, (0, y))
            else:
                surface.blit(self.bottom, (0, y))

        if self.style == "overworld":
            for palm in self.palms:
                surface.blit(palm[0], palm[1])
            for cloud in self.clouds:
                surface.blit(cloud[0], cloud[1])


class Water:
    def __init__(self, top, level_width):
        water_start = -SCREEN_WIDTH
        water_tile_width = 192
        tile_x_amount = int((level_width + SCREEN_WIDTH * 2) / water_tile_width)
        self.water_sprites = pygame.sprite.Group()

        for tile in range(tile_x_amount):
            x = tile * water_tile_width + water_start
            y = top
            sprite = AnimatedTile(192, x, y, "../graphics/decoration/water")
            self.water_sprites.add(sprite)

    def draw(self, surface, shift):
        self.water_sprites.update(shift)
        self.water_sprites.draw(surface)


class Clouds:
    def __init__(self, horizon, level_width, cloud_number):
        cloud_surf_list = import_folder("../graphics/decoration/clouds")
        min_x = -SCREEN_WIDTH
        max_x = level_width + SCREEN_WIDTH
        min_y = 0
        max_y = horizon
        self.cloud_sprites = pygame.sprite.Group()

        clouds = choices(cloud_surf_list)
        for cloud in clouds:
            x = randint(min_x, max_x)
            y = randint(min_y, max_y)
            sprite = StaticTile(0, x, y, cloud)
            self.cloud_sprites.add(sprite)

    def draw(self, surface, shift):
        self.cloud_sprites.update(shift)
        self.cloud_sprites.draw(surface)
