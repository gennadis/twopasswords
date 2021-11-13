"""
# TODO: should place some nice text here...

This module is responsible for TUI selection
either will it be Registration TUI if no 
Database and user's picture files were found
or will it be Authentification TUI if such files exists.

...

"""

from os import path

from views import tui_auth
from views import tui_first_run
from config import config_loader

# load configuration
file_paths, email_settings = config_loader.load()

face_is_registered: bool = path.exists(file_paths["user_image"])
database_is_created: bool = path.exists(file_paths["db_path"])


def select_tui():
    """
    Check if Database and user's face picture
    files exists and start appropriate TUI.

    """

    if face_is_registered and database_is_created:
        tui_auth.start_auth()
    else:
        tui_first_run.start_registration()


if __name__ == "__main__":
    select_tui()
