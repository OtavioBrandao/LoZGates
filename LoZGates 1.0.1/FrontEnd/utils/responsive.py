"""Calculos de layout independentes de Tk para janelas e paineis responsivos."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WindowLayout:
    width: int
    height: int
    x: int
    y: int
    minimum_width: int
    minimum_height: int

    @property
    def geometry(self):
        return f"{self.width}x{self.height}+{self.x}+{self.y}"


def calculate_window_layout(
    screen_width,
    screen_height,
    preferred=(1280, 800),
    minimum=(720, 520),
    margin=40,
):
    screen_width = max(320, int(screen_width))
    screen_height = max(240, int(screen_height))
    available_width = max(320, screen_width - margin)
    available_height = max(240, screen_height - margin)
    minimum_width = min(int(minimum[0]), available_width)
    minimum_height = min(int(minimum[1]), available_height)
    width = max(minimum_width, min(int(preferred[0]), available_width))
    height = max(minimum_height, min(int(preferred[1]), available_height))
    return WindowLayout(
        width=width,
        height=height,
        x=max(0, (screen_width - width) // 2),
        y=max(0, (screen_height - height) // 2),
        minimum_width=minimum_width,
        minimum_height=minimum_height,
    )


def calculate_wraplength(container_width, padding=80, minimum=240, maximum=900):
    return max(minimum, min(maximum, int(container_width) - padding))


def responsive_columns(container_width, item_minimum=230, maximum=3):
    usable_width = max(item_minimum, int(container_width))
    return max(1, min(maximum, usable_width // item_minimum))
