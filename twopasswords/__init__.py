from os import path

from twopasswords.config.config import load_config
from twopasswords.views_handler import VIEWS_HANDLER


def check_registration():
    """
    Check if Database and user's face picture
    files exists and start appropriate TUI.

    """

    file_paths = load_config()[0]
    face_is_registered = path.exists(file_paths["user_image"])
    database_is_created = path.exists(file_paths["db_path"])

    if face_is_registered and database_is_created:
        return True

    return False


def main():
    """
    Check registration and start TwoPasswords.
    """

    if check_registration():
        VIEWS_HANDLER.open_view_authentication()

    VIEWS_HANDLER.open_view_registration()
