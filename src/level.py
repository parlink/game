import pygame
from utils import import_csv_layout, import_cut_graphics
from settings import TILE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from tiles import Tile, StaticTile, Soul
from enemy import MinionEnemy, AngelEnemy, BossEnemy
from decoration import Sky, Water, Clouds
from player import Player
from particles import ParticleEffect
from game_data import levels


class Level:
    def __init__(
        self, current_level, surface, create_overworld, change_souls, change_health
    ):
        # general setup
        self.display_surface = surface
        self.world_shift = 0
        self.current_x = None

        # overworld connection
        self.create_overworld = create_overworld
        self.current_level = current_level
        level_data = levels[self.current_level]
        self.new_max_level = level_data["unlock"]

        # player
        player_layout = import_csv_layout(level_data["player"])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, change_health)

        # user interface
        self.change_souls = change_souls

        # dust
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.player_on_ground = False

        # explosion particles
        self.explosion_sprites = pygame.sprite.Group()

        # terrain setup
        terrain_layout = import_csv_layout(level_data["terrain"])
        self.terrain_sprites = self.create_tile_group(terrain_layout, "terrain")

        # souls
        soul_layout = import_csv_layout(level_data["souls"])
        self.soul_sprites = self.create_tile_group(soul_layout, "souls")

        self.enemy_sprites = pygame.sprite.Group()

        # enemy
        for enemy in ["angel_enemy", "minion_enemy"]:
            if enemy in level_data:
                enemy_layout = import_csv_layout(level_data[enemy])
                enemy_sprites = self.create_tile_group(enemy_layout, enemy)
                self.enemy_sprites.add(enemy_sprites)

        # constraint
        constraint_layout = import_csv_layout(level_data["constraints"])
        self.constraint_sprites = self.create_tile_group(
            constraint_layout, "constraint"
        )

        # decoration
        self.sky = Sky(8)
        level_width = len(terrain_layout[0]) * TILE_SIZE
        self.water = Water(SCREEN_HEIGHT - 20, level_width)
        self.clouds = Clouds(400, level_width, 30)

    def create_tile_group(self, layout, tile_type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != "-1":
                    x = col_index * TILE_SIZE
                    y = row_index * TILE_SIZE

                    if tile_type == "terrain":
                        terrain_tile_list = import_cut_graphics(
                            "../graphics/terrain/terrain_tiles.png"
                        )
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(TILE_SIZE, x, y, tile_surface)

                    if tile_type == "souls":
                        if val == "0":
                            sprite = Soul(TILE_SIZE, x, y, "../graphics/souls/gold", 5)
                        if val == "1":
                            sprite = Soul(
                                TILE_SIZE, x, y, "../graphics/souls/silver", 1
                            )

                    if tile_type == "minion_enemy":
                        sprite = MinionEnemy(TILE_SIZE, x, y)

                    if tile_type == "angel_enemy":
                        sprite = AngelEnemy(TILE_SIZE, x, y)

                    #if tile_type == "boss_enemy":
                        #sprite = HeavyEnemy(TILE_SIZE, x, y)

                    if tile_type == "constraint":
                        sprite = Tile(TILE_SIZE, x, y)

                    sprite_group.add(sprite)

        return sprite_group

    def player_setup(self, layout, change_health):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * TILE_SIZE
                y = row_index * TILE_SIZE
                if val == "0":
                    sprite = Player(
                        (x, y),
                        self.display_surface,
                        self.create_jump_particles,
                        change_health,
                    )
                    self.player.add(sprite)
                if val == "1":
                    portal_surface = pygame.image.load(
                        "../graphics/character/portal.png"
                    ).convert_alpha()
                    sprite = StaticTile(TILE_SIZE, x, y, portal_surface)
                    self.goal.add(sprite)

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraint_sprites, False):
                enemy.reverse()

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(10, 5)
        else:
            pos += pygame.math.Vector2(10, -5)
        jump_particle_sprite = ParticleEffect(pos, "jump")
        self.dust_sprite.add(jump_particle_sprite)

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.rect.x += player.direction.x * player.speed
        collidable_sprites = self.terrain_sprites.sprites()
        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.x < 0:
                    player.rect.left = sprite.rect.right
                    player.on_left = True
                    self.current_x = player.rect.left
                elif player.direction.x > 0:
                    player.rect.right = sprite.rect.left
                    player.on_right = True
                    self.current_x = player.rect.right

        if player.on_left and (
            player.rect.left < self.current_x or player.direction.x >= 0
        ):
            player.on_left = False
        if player.on_right and (
            player.rect.right > self.current_x or player.direction.x <= 0
        ):
            player.on_right = False

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()
        collidable_sprites = self.terrain_sprites.sprites()

        for sprite in collidable_sprites:
            if sprite.rect.colliderect(player.rect):
                if player.direction.y > 0:
                    player.rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True

        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        if player.on_ceiling and player.direction.y > 0.1:
            player.on_ceiling = False

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        if player_x < SCREEN_WIDTH / 4 and direction_x < 0:
            self.world_shift = 8
            player.speed = 0
        elif player_x > SCREEN_WIDTH - (SCREEN_WIDTH / 4) and direction_x > 0:
            self.world_shift = -8
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False

    def create_landing_dust(self):
        if (
            not self.player_on_ground
            and self.player.sprite.on_ground
            and not self.dust_sprite.sprites()
        ):
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(10, 15)
            else:
                offset = pygame.math.Vector2(-10, 15)
            fall_dust_particle = ParticleEffect(
                self.player.sprite.rect.midbottom - offset, "land"
            )
            self.dust_sprite.add(fall_dust_particle)

    def check_death(self):
        if self.player.sprite.rect.top > SCREEN_HEIGHT:
            self.create_overworld(self.current_level, 0)

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.create_overworld(self.current_level, self.new_max_level)

    def check_soul_collisions(self):
        collided_souls = pygame.sprite.spritecollide(
            self.player.sprite, self.soul_sprites, True
        )
        if collided_souls:
            for soul in collided_souls:
                self.change_souls(soul.value)

    def check_enemy_collisions(self):
        enemy_collisions = pygame.sprite.spritecollide(
            self.player.sprite, self.enemy_sprites, False
        )

        if enemy_collisions:
            for enemy in enemy_collisions:
                enemy_center = enemy.rect.centery
                enemy_top = enemy.rect.top
                player_bottom = self.player.sprite.rect.bottom
                if (
                    enemy_top < player_bottom < enemy_center
                    and self.player.sprite.direction.y >= 0
                ):
                    self.player.sprite.direction.y = -15
                    explosion_sprite = ParticleEffect(enemy.rect.center, "explosion")
                    self.explosion_sprites.add(explosion_sprite)
                    enemy.kill()
                else:
                    self.player.sprite.get_damage(enemy=enemy)

    def run(self):
        # run the entire game / level

        # sky
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)

        # terrain
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)

        # enemy
        self.enemy_sprites.update(self.world_shift)
        self.constraint_sprites.update(self.world_shift)
        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)
        self.explosion_sprites.update(self.world_shift)
        self.explosion_sprites.draw(self.display_surface)

        # souls
        self.soul_sprites.update(self.world_shift)
        self.soul_sprites.draw(self.display_surface)

        # dust particles
        self.dust_sprite.update(self.world_shift)
        self.dust_sprite.draw(self.display_surface)

        # player sprites
        self.player.update()
        self.horizontal_movement_collision()

        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()

        self.scroll_x()
        self.player.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.check_death()
        self.check_win()

        self.check_soul_collisions()
        self.check_enemy_collisions()

        # water
        self.water.draw(self.display_surface, self.world_shift)
