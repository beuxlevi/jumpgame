import math
import random
import sys
from dataclasses import dataclass

import pygame

# Screen dimensions (16:9 portrait)
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 854

# Player constants
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 60
ACC_GROUND = 1.0
ACC_AIR = 0.5
MAX_SPEED = 5
JUMP_VELOCITY = 22
GRAVITY = -1.0

# Platform constants
PLATFORM_WIDTH = 120
PLATFORM_HEIGHT = 22
INITIAL_GAP_MIN = 110
INITIAL_GAP_MAX = 130
INITIAL_OFFSET_MAX = 140
MAX_GAP_CAP = int(0.85 * (JUMP_VELOCITY ** 2) / (-2 * GRAVITY))

AUTOSCROLL_SPEED = 1.6
INCREASE_EVERY = 10
GAP_INCREASE = 10
OFFSET_INCREASE = 10
SCROLL_INCREASE = 0.1


@dataclass
class Platform:
    x: float
    y: float  # top y coordinate in world space (bottom-left origin)
    passed: bool = False

    @property
    def rect(self):
        return pygame.Rect(self.x, SCREEN_HEIGHT - self.y, PLATFORM_WIDTH, PLATFORM_HEIGHT)


class Player:
    def __init__(self):
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.x = SCREEN_WIDTH / 2 - self.width / 2
        self.y = 0  # bottom y coordinate
        self.vx = 0
        self.vy = 0
        self.grounded = True

    def update(self, keys, dt, platforms, camera_y):
        # Horizontal movement
        target = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target -= MAX_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target += MAX_SPEED

        if self.grounded:
            self.vx += ACC_GROUND * (target - self.vx)
            self.vx *= 0.8 if abs(target) < 0.1 else 1
        else:
            self.vx += ACC_AIR * (target - self.vx)
            self.vx *= 0.98

        self.x += self.vx
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

        # Gravity
        self.vy += GRAVITY
        self.y += self.vy

        # Collisions with platforms
        new_ground = False
        for p in platforms:
            if self.vy <= 0 and self.y - self.vy > p.y and self.y <= p.y:
                if self.x + self.width > p.x and self.x < p.x + PLATFORM_WIDTH:
                    self.y = p.y
                    self.vy = 0
                    new_ground = True
        self.grounded = new_ground

    def jump(self):
        if self.grounded:
            self.vy = JUMP_VELOCITY
            self.grounded = False

    def draw(self, surface, camera_y):
        screen_y = SCREEN_HEIGHT - ((self.y - camera_y) + self.height)
        rect = pygame.Rect(self.x, screen_y, self.width, self.height)
        pygame.draw.rect(surface, (200, 50, 50), rect)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Jump")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.platforms = [Platform(0, 0)]  # floor
        self.last_platform_x = 0
        self.last_platform_y = 0
        self.camera_y = 0
        self.autoscroll = False
        self.scroll_speed = AUTOSCROLL_SPEED
        self.score = 0
        self.spawn_platforms()

    def spawn_platforms(self):
        gap_max = INITIAL_GAP_MAX + (self.score // INCREASE_EVERY) * GAP_INCREASE
        gap_max = min(gap_max, MAX_GAP_CAP)
        offset_max = INITIAL_OFFSET_MAX + (self.score // INCREASE_EVERY) * OFFSET_INCREASE
        while self.last_platform_y < self.camera_y + SCREEN_HEIGHT * 2:
            gap = random.randint(INITIAL_GAP_MIN, gap_max)
            new_y = self.last_platform_y + gap
            dx = random.randint(-offset_max, offset_max)
            new_x = max(0, min(self.last_platform_x + dx, SCREEN_WIDTH - PLATFORM_WIDTH))
            self.platforms.append(Platform(new_x, new_y))
            self.last_platform_x = new_x
            self.last_platform_y = new_y

    def remove_platforms(self):
        self.platforms = [p for p in self.platforms if p.y > self.camera_y - 100]

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.player.jump()

            keys = pygame.key.get_pressed()
            self.player.update(keys, dt, self.platforms, self.camera_y)

            # Autoscroll check
            if not self.autoscroll and (self.player.y - self.camera_y) > SCREEN_HEIGHT / 2:
                self.autoscroll = True
            if self.autoscroll:
                inc = self.scroll_speed
                self.camera_y += inc
                if self.score and self.score % INCREASE_EVERY == 0:
                    self.scroll_speed += SCROLL_INCREASE

            # Check fail conditions
            if self.autoscroll and self.player.y + self.player.height < self.camera_y:
                running = False

            # Scoring
            for p in self.platforms:
                if not p.passed and self.player.y > p.y:
                    p.passed = True
                    if p.y > 0:
                        self.score += 1

            self.spawn_platforms()
            self.remove_platforms()

            # Drawing
            self.screen.fill((30, 30, 40))
            for p in self.platforms:
                screen_y = SCREEN_HEIGHT - ((p.y - self.camera_y))
                rect = pygame.Rect(p.x, screen_y, PLATFORM_WIDTH, PLATFORM_HEIGHT)
                pygame.draw.rect(self.screen, (200, 200, 200), rect)
            self.player.draw(self.screen, self.camera_y)

            font = pygame.font.SysFont(None, 36)
            score_surf = font.render(str(self.score), True, (255, 255, 255))
            self.screen.blit(score_surf, (10, 10))
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    Game().run()
