import unittest

from FrontEnd.utils.responsive import (
    calculate_window_layout,
    calculate_wraplength,
    responsive_columns,
)


class ResponsiveLayoutTests(unittest.TestCase):
    def test_window_layout_stays_inside_common_screen_sizes(self):
        for screen_width, screen_height in (
            (640, 480),
            (1024, 600),
            (1366, 768),
            (1920, 1080),
            (3840, 2160),
        ):
            with self.subTest(screen=(screen_width, screen_height)):
                layout = calculate_window_layout(screen_width, screen_height)
                self.assertGreaterEqual(layout.x, 0)
                self.assertGreaterEqual(layout.y, 0)
                self.assertLessEqual(layout.x + layout.width, screen_width)
                self.assertLessEqual(layout.y + layout.height, screen_height)
                self.assertLessEqual(layout.minimum_width, layout.width)
                self.assertLessEqual(layout.minimum_height, layout.height)

    def test_wraplength_and_columns_follow_available_width(self):
        self.assertEqual(responsive_columns(400), 1)
        self.assertEqual(responsive_columns(600), 2)
        self.assertEqual(responsive_columns(1200), 3)
        self.assertEqual(calculate_wraplength(320), 240)
        self.assertEqual(calculate_wraplength(2000), 900)


if __name__ == "__main__":
    unittest.main()
