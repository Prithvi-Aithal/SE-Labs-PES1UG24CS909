import math
import pygame


class Rope:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center_y = screen_height // 2
        self.marker_x = screen_width // 2

        self.left_win_x = 180
        self.right_win_x = screen_width - 180
        self.pull_step = 12

        self.rope_left_x = 60
        self.rope_right_x = screen_width - 60
        # 0 = slack (rope sags), 1 = full struggle (rope hums/vibrates)
        self.tension = 0.0
        self.max_sag = 18
        self.max_vibration = 6

    def pull_left(self, strength=1.0):
        self.marker_x -= int(self.pull_step * strength)

    def pull_right(self, strength=1.0):
        self.marker_x += int(self.pull_step * strength)

    def check_winner(self):
        if self.marker_x <= self.left_win_x:
            return "PLAYER"
        if self.marker_x >= self.right_win_x:
            return "COMPUTER"
        return None

    def rope_y(self, x):
        """Vertical position of the rope at x, including sag and vibration."""
        span = self.rope_right_x - self.rope_left_x
        u = min(1.0, max(0.0, (x - self.rope_left_x) / span))
        # Ends stay pinned; displacement is largest mid-rope
        envelope = math.sin(math.pi * u)
        sag = self.max_sag * (1.0 - self.tension) * envelope
        phase = pygame.time.get_ticks() * 0.05
        hum = self.max_vibration * self.tension * envelope * math.sin(x * 0.12 + phase)
        return self.center_y + sag + hum

    def reset(self):
        self.marker_x = float(self.screen_width // 2)
        self.velocity = 0.0

    def render(self, surface):
        # Rope brightens slightly as it is pulled taut
        t = self.tension
        rope_color = (int(180 + 40 * t), int(140 + 20 * t), int(90 - 20 * t))
        points = [
            (x, self.rope_y(x))
            for x in range(self.rope_left_x, self.rope_right_x + 1, 8)
        ]
        pygame.draw.lines(surface, rope_color, False, points, 10)

        pygame.draw.line(
            surface,
            (50, 200, 50),
            (self.left_win_x, self.center_y - 40),
            (self.left_win_x, self.center_y + 40),
            4
        )
        pygame.draw.line(
            surface,
            (200, 50, 50),
            (self.right_win_x, self.center_y - 40),
            (self.right_win_x, self.center_y + 40),
            4
        )

        pygame.draw.line(
            surface,
            (120, 120, 120),
            (self.screen_width // 2, self.center_y - 20),
            (self.screen_width // 2, self.center_y + 20),
            2
        )

        flag_y = int(self.rope_y(self.marker_x))
        flag_rect = pygame.Rect(int(self.marker_x) - 12, flag_y - 24, 24, 48)
        pygame.draw.rect(surface, (230, 40, 40), flag_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 255, 255), flag_rect, width=2, border_radius=4)