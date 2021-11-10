from os import environ, path
from dotenv import load_dotenv

from views.tui_auth import start_auth
from views.tui_first_run import start_registration


load_dotenv()
DB_PATH = environ.get("DB_PATH")
USER_PICTURE = environ.get("USER_FACE")

face_is_registered: bool = path.exists(USER_PICTURE)
database_is_created: bool = path.exists(DB_PATH)


def check_if_new_user():
    if face_is_registered and database_is_created:
        start_auth()
    else:
        start_registration()


if __name__ == "__main__":
    check_if_new_user()
