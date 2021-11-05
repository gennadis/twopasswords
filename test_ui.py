import py_cui

__ui_stack = []


def ui_push(ui, screen):
    __ui_stack.append(screen)

    screen.root.add_key_command(py_cui.keys.KEY_Q_LOWER, lambda: ui_pop(ui))
    screen.root.add_key_command(py_cui.keys.KEY_Q_UPPER, lambda: ui_pop(ui))

    screen.apply()


def ui_pop(ui):
    __ui_stack.pop()

    if len(__ui_stack) <= 0:
        ui.stop()
        return

    screen = __ui_stack[len(__ui_stack) - 1]
    screen.apply()

    ui.lose_focus()
