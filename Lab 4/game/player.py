import math
import pygame


class Puller:
    """Represents a puller character anchor on either side of the rope."""

    MAX_LEAN_DEG = 28
    LEAN_SMOOTHING = 0.15

    def __init__(self, x, y, color, label, facing=1):
        self.x = x
        self.y = y
        self.color = color
        self.label = label
        # +1 if the rope (and opponent) is to the right, -1 if to the left
        self.facing = facing
        self.lean = 0.0
        self.font = pygame.font.SysFont(None, 24)

    def lean_toward(self, target):
        """Ease the lean amount (0 = upright, 1 = full lean back) toward target."""
        self.lean += (target - self.lean) * self.LEAN_SMOOTHING

    def render(self, surface, grip_y=None):
        """Draw avatar leaning back away from the rope, plus arms and label."""
        angle = math.radians(self.MAX_LEAN_DEG * self.lean)
        # Unit vector from feet toward head; leaning back tilts it away from the rope
        up = (-self.facing * math.sin(angle), -math.cos(angle))
        side = (-up[1], up[0])

        feet = (self.x, self.y + 35)

        def along(dist, offset=0.0):
            return (
                feet[0] + up[0] * dist + side[0] * offset,
                feet[1] + up[1] * dist + side[1] * offset,
            )

        # Body
        body = [along(0, -20), along(0, 20), along(70, 20), along(70, -20)]
        pygame.draw.polygon(surface, self.color, body)

        # Arms reaching forward to grip the rope
        if grip_y is not None:
            shoulder = along(58)
            grip = (self.x + self.facing * 28, grip_y)
            pygame.draw.line(surface, (240, 210, 180), shoulder, grip, 6)

        # Head
        head = along(85)
        pygame.draw.circle(surface, (240, 210, 180), (int(head[0]), int(head[1])), 16)

        # Name / control tag
        label_surf = self.font.render(self.label, True, (240, 240, 240))
        surface.blit(label_surf, (self.x - label_surf.get_width() // 2, self.y + 45))
