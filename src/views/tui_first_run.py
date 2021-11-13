"""
# TODO: should place some nice text here...

This module is responsible for managing operations
needed for new user registration:
- registers new user face
- creates new database with entered password
...

"""

import logging
from time import sleep

import py_cui

from utils import database
from views import tui_main
from config import config_loader
from utils.facescan import FaceScan

# load configuration
file_paths, email_settings = config_loader.load()


class RegistrationTUI:
    """
    A class used to register new user:
        - register new user's face
        - create new database with entered password

    Attributes
    ----------
    root : py_cui.PyCUI
        Instance of a base PyCUI main interface class
    db_password : str
        Password to a Database that will be used
        as a master password to a program.
    welcome_block
        Welcome text block with some info regarding
        registration steps needed to be done.
    welcome_text : list
        List of strings of text with registration info.
    take_picure_button
        Button that takes picture and saves it on a disk
    create_database_button
        Button that asks for a new master
        password and creates a Database
    next_button
        Button that opens main TwoPasswords App
    show_create_database_popup
        Shows popup that asks to enter new master password

    Methods
    -------
    proceed_to_app
        Proceeds to main TwoPasswords app if registration
        went successfully, else shows error popup.
    populate_welcome_text
        Populates welcome block with text
    take_new_user_image
        Takes new user photo and saves it on a disk
    show_create_database_popup
        Shows popup with new master password and confirmation inputs
    check_new_pragma
        Checks new master password and sets it to a database.

    """

    def __init__(self, root: py_cui.PyCUI):
        """
        root : py_cui.PyCUI
            Instance of a base PyCUI main interface class
        db_password : str
            Password to a Database that will be used
            as a master password to a program.
        welcome_block
            Welcome text block with some info regarding
            registration steps needed to be done.
        welcome_text : list
            List of strings of text with registration info.
        take_picure_button
            Button that takes picture and saves it on a disk
        create_database_button
            Button that asks for a new master
            password and creates a Database
        next_button
            Button that opens main TwoPasswords App
        show_create_database_popup
            Shows popup that asks to enter new master password

        """

        self.root = root
        self.db_password = None
        self.root.set_title(f"TwoPasswords")

        ################ WELCOME TEXT BLOCK ################
        self.welcome_block = self.root.add_scroll_menu("Welcome!", 0, 0, 3)
        self.welcome_text = [
            "",
            "To start using TwoPasswords,",
            "complete the following tasks:",
            "",
            "1. Scan and register your face",
            "2. Create a database and your master password",
            "3. Proceed by hitting the Next button",
        ]
        self.welcome_block.add_text_color_rule(
            "DONE", py_cui.CYAN_ON_BLACK, "startswith"
        )
        self.populate_welcome_text()

        ################ TAKE PICTURE BUTTON ################
        self.take_picture_button = self.root.add_button(
            "Step 1: Register your face", 0, 1, command=self.take_new_user_image
        )
        self.take_picture_button.set_color(py_cui.WHITE_ON_BLACK)

        ################ CREATE DATABASE BUTTON ################
        self.create_database_button = self.root.add_button(
            "Step 2: Create a database",
            1,
            1,
            command=self.show_create_database_popup,
        )
        self.create_database_button.set_color(py_cui.WHITE_ON_BLACK)

        ################ EXIT BUTTON ################
        self.next_button = self.root.add_button(
            "Next", 2, 1, command=self.proceed_to_app
        )
        self.next_button.set_color(py_cui.GREEN_ON_BLACK)

        self.root.set_selected_widget(1)

    def proceed_to_app(self):
        """
        Stops current PyCUI instance and proceeds
        to main TwoPasswords app if registration
        went successfully, else shows error popup.

        """

        if self.db_password:
            self.root.forget_widget(self.welcome_block)
            self.root.forget_widget(self.take_picture_button)
            self.root.forget_widget(self.create_database_button)
            self.root.forget_widget(self.next_button)
            self.root.stop()
            tui_main.start_tui(self.db_password)
        else:
            self.root.show_error_popup("Error", "Registration was not completed")

    def populate_welcome_text(self):
        """
        Populates welcome block with text

        """
        self.welcome_block.clear()
        self.welcome_block.add_item_list(self.welcome_text)

    def take_new_user_image(self):
        """
        Takes new user photo and saves it on a disk

        """

        FaceScan("", file_paths["user_image"]).take_picture()
        sleep(1)
        self.root.show_message_popup("Done!", "Face registered successfully")

        self.welcome_text[4] = "DONE --> " + self.welcome_text[4]
        self.populate_welcome_text()
        self.root.set_selected_widget(2)

    def show_create_database_popup(self):
        """
        Shows popup with new master
        password and confirmation fields.

        """

        entry_fields = ["Master password", "Confirm master password"]
        self.root.show_form_popup(
            "Create your master password",
            entry_fields,
            entry_fields,
            required=entry_fields,
            callback=self.check_new_pragma,
        )

    def check_new_pragma(self, form_output):
        """
        Checks new master password and creates new Database
        with such password as a master password.
        If password does not match, shows error popup.

        Note:
        show_create_database_popup returns
        form_output as a dictionary, hence
        the implementation with dict keys.

        Parameters
        ----------
        form_output : dict
            The output from a show_create_database_popup.

        """

        entry1, entry2 = (
            form_output["Master password"],
            form_output["Confirm master password"],
        )

        if entry1 == entry2:
            self.root.show_message_popup("Done!", f"Your master password is: {entry1}")
            database.create_db(file_paths["db_path"], entry1, to_create=True)

            self.db_password = entry1

            self.welcome_text[5] = "DONE --> " + self.welcome_text[5]
            self.populate_welcome_text()
            self.root.set_selected_widget(3)

        else:
            self.root.show_error_popup(
                "Error",
                "Password and confirm password does not match",
            )


def start_registration():
    """
    Runs Registration TUI.

    """

    root = py_cui.PyCUI(3, 2)
    root.toggle_unicode_borders()
    # root.enable_logging(logging_level=logging.DEBUG)
    frame = RegistrationTUI(root)
    root.start()


if __name__ == "__main__":
    start_registration()
