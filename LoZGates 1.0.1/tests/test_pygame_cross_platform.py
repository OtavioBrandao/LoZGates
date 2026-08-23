import os
import unittest
from unittest.mock import patch

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from BackEnd.circuito_logico.interactive.palette import ComponentPalette
from BackEnd.circuito_logico.interactive.interactive_circuit import (
    CircuitoInterativoManual,
)
from BackEnd.circuito_logico.platform_support import (
    fit_surface_size,
    select_sdl_video_driver,
)
from BackEnd.circuito_logico.rendering.camera import Camera
from BackEnd.circuito_logico.rendering.circuit_renderer import (
    desenhar_circuito_logico_base,
)
from BackEnd.circuito_logico.rendering.drawer import CircuitDrawer


class PlatformSupportTests(unittest.TestCase):
    def test_driver_selection_is_platform_aware(self):
        self.assertEqual(
            select_sdl_video_driver("win32", {}),
            "windows",
        )
        self.assertEqual(
            select_sdl_video_driver("linux", {"DISPLAY": ":0"}),
            "x11",
        )
        self.assertIsNone(select_sdl_video_driver("linux", {}))
        self.assertEqual(
            select_sdl_video_driver("linux", {"SDL_VIDEODRIVER": "dummy"}),
            "dummy",
        )

    def test_surface_size_uses_frame_dimensions_with_safe_floor(self):
        self.assertEqual(fit_surface_size(200, 100), (320, 240))
        self.assertEqual(fit_surface_size(1024, 576), (1024, 576))


class ResponsivePygameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_camera_zoom_keeps_pointer_world_position_stable(self):
        camera = Camera(800, 600)
        pointer = (615, 245)
        before = camera.screen_to_world(pointer)
        camera.zoom_at(pointer, 0.5)
        after = camera.screen_to_world(pointer)
        self.assertAlmostEqual(before[0], after[0])
        self.assertAlmostEqual(before[1], after[1])

        camera.update_viewport(1280, 720)
        self.assertEqual((camera.screen_width, camera.screen_height), (1280, 720))

    def test_palette_stays_inside_small_and_large_surfaces(self):
        palette = ComponentPalette(320, 240)
        for width, height in ((320, 240), (800, 600), (1920, 1080)):
            with self.subTest(size=(width, height)):
                palette.resize(width, height)
                self.assertLessEqual(palette.x + palette.width, width)
                self.assertLessEqual(palette.y + palette.height, height)
                last_button = palette.get_button_rect(len(palette.components) - 1)
                self.assertLessEqual(last_button.bottom, palette.y + palette.height)

    def test_static_renderer_draws_at_multiple_resolutions(self):
        for width, height in ((640, 360), (1280, 720)):
            with self.subTest(size=(width, height)):
                surface = pygame.Surface((width, height))
                camera = Camera(width, height)
                drawer = CircuitDrawer(surface, camera)
                desenhar_circuito_logico_base("(A*B)+~C", drawer, width, height)
                bounding_rect = surface.get_bounding_rect()
                self.assertGreater(bounding_rect.width, 0)
                self.assertGreater(bounding_rect.height, 0)

    def test_circuit_expression_evaluation_does_not_use_python_eval(self):
        circuit = object.__new__(CircuitoInterativoManual)
        self.assertTrue(circuit.evaluate_expression("(A*B)+~C", {"A": True, "B": True, "C": True}))
        with patch("os.system") as system_call:
            with self.assertLogs(
                "BackEnd.circuito_logico.interactive.interactive_circuit",
                level="ERROR",
            ):
                result = circuit.evaluate_expression(
                    "__import__('os').system('unsafe')", {}
                )
        system_call.assert_not_called()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
