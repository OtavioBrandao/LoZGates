import unittest

from FrontEnd.app.navigation import (
    NavigationController,
    CIRCUIT_TAB,
    EXPRESSION_TAB,
    INTERACTIVE_CIRCUIT_TAB,
)


class FakeFrame:
    def __init__(self):
        self.raise_count = 0

    def tkraise(self):
        self.raise_count += 1


class FakeTabview:
    def __init__(self):
        self.selected = None

    def set(self, value):
        self.selected = value


class NavigationControllerTests(unittest.TestCase):
    def test_explicit_circuit_action_always_selects_circuit_tab(self):
        tabs_frame = FakeFrame()
        tabview = FakeTabview()
        navigation = NavigationController(tabs_frame, tabview)

        navigation.show_tab("expression")
        self.assertEqual(tabview.selected, EXPRESSION_TAB)
        navigation.show_tab("circuit")

        self.assertEqual(tabview.selected, CIRCUIT_TAB)
        self.assertEqual(navigation.current_screen_name, "circuit")
        self.assertEqual(tabs_frame.raise_count, 2)

    def test_normal_navigation_remains_available_after_circuit(self):
        tabs_frame = FakeFrame()
        other_frame = FakeFrame()
        tabview = FakeTabview()
        navigation = NavigationController(
            tabs_frame,
            tabview,
            frame_names={other_frame: "home"},
        )

        navigation.show_tab("circuit")
        navigation.show_tab("expression")
        navigation.show_frame(other_frame)

        self.assertEqual(navigation.current_screen_name, "home")
        self.assertEqual(other_frame.raise_count, 1)


if __name__ == "__main__":
    unittest.main()
