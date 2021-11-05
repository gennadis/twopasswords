import py_cui
from auth_screen import AuthScreen
from ui import ui_pop, ui_push


if __name__ == "__main__":
    root = py_cui.PyCUI(8, 8)
    root.toggle_unicode_borders()
    root._exit_key = None
    ui_push(root, AuthScreen(root))
    root.start()
