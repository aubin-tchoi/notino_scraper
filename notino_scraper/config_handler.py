import os

from yaml import safe_load, dump, YAMLError


def update_config(config_file: str, key: str, new_value: str) -> None:
    """
    Updates the value associated with the provided key in the yaml config file.

    Args:
        config_file: The path to the yaml config file to use.
        key: The key to update.
        new_value: The value to update with.
    """
    with open(config_file, "r") as stream:
        config = safe_load(stream)

    config[key] = new_value

    with open(config_file, "w") as stream:
        try:
            dump(config, stream, default_flow_style=False, allow_unicode=True)
        except YAMLError as exc:
            print(exc)


def update_datafile(config_file: str, new_datafile: str) -> None:
    """
    Updates the value associated with key "datafile" in the yaml config file.

    Args:
        config_file: The path to the yaml config file to use.
        new_datafile: The value to replace with.
    """
    if not new_datafile.endswith(".json"):
        new_datafile += ".json"
    assert os.path.isfile(new_datafile), "Invalid file path provided."

    update_config(config_file, "datafile", new_datafile)


def update_img_folder(config_file: str, new_folder: str) -> None:
    """
    Updates the value associated with key "img_folder" in the yaml config file.

    Args:
        config_file: The path to the yaml config file to use.
        new_folder: The value to replace with.
    """
    assert os.path.isdir(new_folder), "Invalid folder path provided."

    update_config(config_file, "img_folder", new_folder)


def set_config_parameters() -> None:
    """
    Sets every existing parameter in the configuration by asking for user input on each of them.
    Also validates the input and asks for it again if an incorrect value is passed.
    """
    config_parameters = [
        (
            "Please specify the path to the output json file (press ENTER to leave it as it is): ",
            update_datafile,
        ),
        (
            "Please specify the folder in which the images will be stored (press ENTER to leave it as it is): ",
            update_img_folder,
        ),
    ]
    for input_message, method in config_parameters:
        # Asking for user input again and again until a correct value is provided or the default value is kept.
        while True:
            try:
                if (user_input := input(input_message)) != "":
                    method(user_input)
                print("Default value will be kept.")
                break
            except AssertionError:
                print("Invalid input, please try again.")
    print("You're all set.")
