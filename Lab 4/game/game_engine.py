import random
import pygame
from game.rope import Rope
from game.player import Puller


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rope = Rope(width, height)
        self.player = Puller(90, height // 2, (50, 120, 220), "PLAYER (A/D)")
        self.computer = Puller(width - 90, height // 2, (220, 80, 50), "COMPUTER")

        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"

        self.computer_pull_cooldown = 180
        self.last_computer_pull = pygame.time.get_ticks()

        # Panic surge: once the player has dragged the flag past this fraction
        # of the way to their goal, the computer ramps toward faster, stronger
        # pulls. Tuned so a fast-mashing player can still win.
        self.panic_threshold = 0.5
        self.panic_min_cooldown = 130
        self.panic_max_strength = 1.35
        self.panic_level = 0.0

        self.font_big = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 26)

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        # A pull registers on every KEYDOWN that differs from the previous
        # pull key. No lock is held until KEYUP, so overlapping presses during
        # fast mashing (D pressed before A is released) still count, and a
        # missed KEYUP can never freeze input.
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_a, pygame.K_d):
            if event.key != self.last_key:
                self.rope.pull_left(1.0)
                self.last_key = event.key

    def update(self):
        if self.game_state != "PLAYING":
            return

        now = pygame.time.get_ticks()
        self.panic_level = self.compute_panic_level()
        cooldown = self.computer_pull_cooldown - (
            self.computer_pull_cooldown - self.panic_min_cooldown
        ) * self.panic_level
        if now - self.last_computer_pull >= cooldown:
            computer_variance = random.uniform(0.7, 1.2)
            strength = computer_variance * (1.0 + (self.panic_max_strength - 1.0) * self.panic_level)
            self.rope.pull_right(strength)
            self.last_computer_pull = now

        result = self.rope.check_winner()
        if result:
            self.winner = result
            self.game_state = "GAME_OVER"

    def compute_panic_level(self):
        """0.0 when calm, rising to 1.0 as the flag nears the player's goal."""
        center = self.width / 2
        progress = (center - self.rope.marker_x) / (center - self.rope.left_win_x)
        if progress <= self.panic_threshold:
            return 0.0
        return min(1.0, (progress - self.panic_threshold) / (1.0 - self.panic_threshold))

    def reset(self):
        self.rope.reset()
        self.panic_level = 0.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"
        self.last_computer_pull = pygame.time.get_ticks()

    def render(self, screen):
        screen.fill((30, 32, 36))

        mud_rect = pygame.Rect(self.width // 2 - 120, self.height // 2 - 80, 240, 160)
        pygame.draw.rect(screen, (45, 38, 30), mud_rect, border_radius=12)

        self.rope.render(screen)
        self.player.render(screen)
        self.computer.render(screen)

        inst_surf = self.font_small.render(
            "Alternate [A] and [D] keys rapidly to pull!", True, (210, 210, 210)
        )
        screen.blit(inst_surf, (self.width // 2 - inst_surf.get_width() // 2, 40))

        if self.game_state == "PLAYING" and self.panic_level > 0:
            # Flash faster as the panic intensifies
            blink_ms = int(400 - 250 * self.panic_level)
            if (pygame.time.get_ticks() // blink_ms) % 2 == 0:
                panic_surf = self.font_small.render(
                    "COMPUTER PANIC SURGE!", True, (255, 140, 40)
                )
                screen.blit(
                    panic_surf,
                    (self.width // 2 - panic_surf.get_width() // 2, self.height - 60)
                )

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            win_text = f"{self.winner} WINS!"
            color = (80, 220, 80) if self.winner == "PLAYER" else (240, 80, 80)
            text_surf = self.font_big.render(win_text, True, color)
            screen.blit(
                text_surf,
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 50)
            )

            restart_surf = self.font_small.render(
                "Press [R] to Play Again", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 10)
            )
