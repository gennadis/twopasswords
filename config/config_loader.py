import yaml


def load():
    with open("config/config.yaml", "r") as file:
        config = yaml.safe_load(file)
        local_paths = config[0]["files"]
        email_settings = config[1]["email"]

    return local_paths, email_settings
