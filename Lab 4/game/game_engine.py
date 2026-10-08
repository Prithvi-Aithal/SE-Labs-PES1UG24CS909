import random
import pygame
from game.rope import Rope
from game.player import Puller


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rope = Rope(width, height)
        self.player = Puller(90, height // 2, (50, 120, 220), "PLAYER (A/D)", facing=1)
        self.computer = Puller(width - 90, height // 2, (220, 80, 50), "COMPUTER", facing=-1)

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

        # Animation state: momentum > 0 favours the computer, < 0 the player.
        # Both decay each frame so they reflect recent pulling activity.
        self.momentum = 0.0
        self.struggle = 0.0
        self.anim_decay = 0.93

        # Match timer; after the limit, sudden death doubles all pulling power
        self.sudden_death_ms = 45_000
        self.match_start = pygame.time.get_ticks()
        self.elapsed_ms = 0
        self.sudden_death = False
        self.power_multiplier = 1.0

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
                self.rope.pull_left(self.power_multiplier)
                self.last_key = event.key
                self.momentum -= self.power_multiplier
                self.struggle += self.power_multiplier

    def update(self):
        if self.game_state != "PLAYING":
            return

        now = pygame.time.get_ticks()
        self.elapsed_ms = now - self.match_start
        if not self.sudden_death and self.elapsed_ms >= self.sudden_death_ms:
            self.sudden_death = True
            self.power_multiplier = 2.0

        self.panic_level = self.compute_panic_level()
        cooldown = self.computer_pull_cooldown - (
            self.computer_pull_cooldown - self.panic_min_cooldown
        ) * self.panic_level
        if now - self.last_computer_pull >= cooldown:
            computer_variance = random.uniform(0.7, 1.2)
            strength = computer_variance * (1.0 + (self.panic_max_strength - 1.0) * self.panic_level)
            strength *= self.power_multiplier
            self.rope.pull_right(strength)
            self.last_computer_pull = now
            self.momentum += strength
            self.struggle += strength

        self.update_animation()

        result = self.rope.check_winner()
        if result:
            self.winner = result
            self.game_state = "GAME_OVER"

    def update_animation(self):
        """Feed recent pulling activity into rope tension and puller lean."""
        self.momentum *= self.anim_decay
        self.struggle *= self.anim_decay

        self.rope.tension = min(1.0, self.struggle / 4.0)

        # Normalised momentum in [-1, 1]; the side winning the pull leans back
        # hardest, while both keep a slight lean from holding the rope.
        lean_bias = max(-1.0, min(1.0, self.momentum / 2.0))
        self.player.lean_toward(0.2 + 0.8 * max(0.0, -lean_bias))
        self.computer.lean_toward(0.2 + 0.8 * max(0.0, lean_bias))

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
        self.momentum = 0.0
        self.struggle = 0.0
        self.rope.tension = 0.0
        self.player.lean = 0.0
        self.computer.lean = 0.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"
        self.last_computer_pull = pygame.time.get_ticks()
        self.match_start = pygame.time.get_ticks()
        self.elapsed_ms = 0
        self.sudden_death = False
        self.power_multiplier = 1.0

    def render(self, screen):
        screen.fill((30, 32, 36))

        mud_rect = pygame.Rect(self.width // 2 - 120, self.height // 2 - 80, 240, 160)
        pygame.draw.rect(screen, (45, 38, 30), mud_rect, border_radius=12)

        self.rope.render(screen)
        self.player.render(screen, self.rope.rope_y(self.player.x + self.player.facing * 28))
        self.computer.render(screen, self.rope.rope_y(self.computer.x + self.computer.facing * 28))

        inst_surf = self.font_small.render(
            "Alternate [A] and [D] keys rapidly to pull!", True, (210, 210, 210)
        )
        screen.blit(inst_surf, (self.width // 2 - inst_surf.get_width() // 2, 40))

        self.render_timer(screen)

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

    def render_timer(self, screen):
        total_s = self.elapsed_ms // 1000
        timer_text = f"TIME {total_s // 60:02d}:{total_s % 60:02d}"
        if self.sudden_death:
            timer_color = (255, 70, 70)
        elif self.sudden_death_ms - self.elapsed_ms <= 10_000:
            timer_color = (255, 200, 60)  # warn during the final 10 seconds
        else:
            timer_color = (210, 210, 210)
        timer_surf = self.font_small.render(timer_text, True, timer_color)
        screen.blit(timer_surf, (self.width // 2 - timer_surf.get_width() // 2, 12))

        if self.sudden_death and self.game_state == "PLAYING":
            sd_surf = self.font_big.render("SUDDEN DEATH  x2 POWER", True, (255, 70, 70))
            screen.blit(sd_surf, (self.width // 2 - sd_surf.get_width() // 2, 70))
