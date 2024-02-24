import pygame
from tiles import AnimatedTile


class AbstractEnemy(AnimatedTile):
    def __init__(self, size, x, y, image_sequence, damage, speed):
        super().__init__(size, x, y, image_sequence)
        self.rect.y += size - self.image.get_size()[1]
        self.damage = damage
        self.speed = speed

    def move(self):
        raise NotImplementedError

    def get_damage(self):
        return self.damage

    def reverse_image(self):
        if self.speed > 0:
            self.image = pygame.transform.flip(self.image, True, False)

    def reverse(self):
        self.speed *= -1

    def update(self, shift):
        super().update(shift)
        self.animate()
        self.move()
        self.reverse_image()


class MinionEnemy(AbstractEnemy):
    def __init__(self, size, x, y):
        super().__init__(
            size, x, y, image_sequence="../graphics/enemy/minion/run", damage=5, speed=5
        )

    def move(self):
        self.rect.x += self.speed


class AngelEnemy(AbstractEnemy):
    def __init__(self, size, x, y):
        super().__init__(
            size, x, y, image_sequence="../graphics/enemy/angel/run", damage=20, speed=3
        )

    def move(self):
        self.rect.x += self.speed

class BossEnemy(AbstractEnemy):
    def __init__(self, size, x, y):
        super().__init__(
            size, x, y, image_sequence="../graphics/enemy/boss/run", damage=100, speed=1
        )

    def move(self):
        self.rect.x += self.speed
