import yaml
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.absolute()


def load_config() -> tuple[dict, dict]:
    """
    Load config from YAML config file.

    Returns
    -------
    tuple[dict, dict]
        a tuple of dictionaries used for calling config parameters:

        local_paths used for storing user's data:
            db_path:    Database file path
            user_image: User face image
            last_image: Last face tried to Auth
            words:      Txt file with 10_000 words for XKCD password generation

        email_settings used for sending Auth reports:
            address:    email address
            password:   email password
            server:     email SMTP server
            port:       email SMTP port
    """

    with open(CONFIG_DIR / "config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
        local_paths: dict = config[0]["files"]
        email_settings: dict = config[1]["email"]

    return local_paths, email_settings
