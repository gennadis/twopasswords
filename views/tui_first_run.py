import logging
from time import sleep

import py_cui

from utils import database
from views import tui_main
from config import config_loader
from utils.facescan import FaceScan


file_paths, email_settings = config_loader.load()


class RegistrationTUI:
    def __init__(self, root: py_cui.PyCUI):
        self.root = root
        self.db_password = None
        self.root.set_title(f"TwoPasswords")

        ################ WELCOME TEXT BLOCK ################
        """
        To start using GitLab with Git, 
        complete the following tasks: 
        Create and sign in to a GitLab account. Open a terminal. Install Git on your computer. Configure ..
        """
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
        self.welcome_block.clear()
        self.welcome_block.add_item_list(self.welcome_text)

    def take_new_user_image(self):
        FaceScan("", file_paths["user_image"]).take_picture()
        sleep(1)
        self.root.show_message_popup("Done!", "Face registered successfully")

        self.welcome_text[4] = "DONE --> " + self.welcome_text[4]
        self.populate_welcome_text()
        self.root.set_selected_widget(2)

    def show_create_database_popup(self):
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
        form_output is a dictionary,
        hence the ugly implementation with different keys
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
    root = py_cui.PyCUI(3, 2)
    root.toggle_unicode_borders()
    # root.enable_logging(logging_level=logging.DEBUG)
    frame = RegistrationTUI(root)
    root.start()


if __name__ == "__main__":
    start_registration()
