from os import path
from tui_auth import start_auth
from tui_first_run import start_registration


face_is_registered = path.exists("user_face.jpg")
database_is_created = path.exists("accounts.sqlite")


def check_if_new_user():
    if not face_is_registered and not database_is_created:
        start_registration()
    else:
        start_auth()


if __name__ == "__main__":
    check_if_new_user()
