from os import path
from tui_first_run import start_registration
from tui import start_tui

face_registered = path.exists("user_face.jpg")
database_created = path.exists("accounts.sqlite")


def check_if_new_user():
    if not face_registered and not database_created:
        start_registration()
    else:
        start_tui()


if __name__ == "__main__":
    check_if_new_user()
