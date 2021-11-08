from dotenv.main import load_dotenv
import py_cui
import dotenv
import logging

from time import sleep


from facescan import FaceScan
from database import create_db

load_dotenv()

user_face_path = "user_face.jpg"
database_path = "accounts.sqlite"


class NewUserRegistration:
    def __init__(self, root: py_cui.PyCUI):
        self.root = root

        ################ WELCOME TEXT BLOCK ################
        self.welcome_block = self.root.add_scroll_menu("Welcome!", 0, 0, 3)
        self.welcome_text = [
            "To start using TwoPasswords App you need to:",
            "",
            "1. Register your face for FaceAuth",
            "2. Create new Database with secure master password",
            "",
            "3. Restart App by hitting the Exit button",
        ]
        self.welcome_block.add_text_color_rule(
            "DONE", py_cui.CYAN_ON_BLACK, "startswith"
        )

        self.populate_welcome_text()

        ################ TAKE PICTURE BUTTON ################
        self.take_picture_button = self.root.add_button(
            "STEP 1 -- Register your face", 0, 1, command=self.take_new_user_picture
        )
        self.take_picture_button.set_color(py_cui.WHITE_ON_BLACK)

        ################ CREATE DATABASE BUTTON ################
        self.create_database_button = self.root.add_button(
            "STEP 2 -- Create new Database",
            1,
            1,
            command=self.show_create_database_popup,
        )
        self.create_database_button.set_color(py_cui.WHITE_ON_BLACK)

        ################ EXIT BUTTON ################
        self.exit_button = self.root.add_button("EXIT", 2, 1, command=self.root.stop)
        self.exit_button.set_color(py_cui.RED_ON_BLACK)

        self.root.set_selected_widget(1)

    def populate_welcome_text(self):
        self.welcome_block.clear()
        self.welcome_block.add_item_list(self.welcome_text)

    def take_new_user_picture(self):
        FaceScan("", "user_face.jpg").take_picture()
        sleep(1)
        self.root.show_message_popup("Done!", "Face registered successfully")

        self.welcome_text[2] = "DONE --> 1. Register your face for FaceAuth"
        self.populate_welcome_text()
        self.root.set_selected_widget(2)

    def show_create_database_popup(self):
        entry_fields = ["New Password", "Confirm new password"]
        self.root.show_form_popup(
            "Enter your Master password",
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
            form_output["New Password"],
            form_output["Confirm new password"],
        )

        if entry1 == entry2:
            dotenv.set_key(
                ".env",
                key_to_set="DB_PASSWORD",
                value_to_set=entry1,
                quote_mode="never",
            )
            self.root.show_message_popup(
                "OK!",
                f"{entry1}, {entry2}",
            )
            create_db(database_path, entry1, to_create=True)

            self.welcome_text[
                3
            ] = "DONE --> 2. Create new Database with secure master password"
            self.populate_welcome_text()
            self.root.set_selected_widget(3)

        else:
            self.root.show_message_popup(
                "Warning!",
                "The confirm password does not match! Try again!",
            )


def start_registration():
    root = py_cui.PyCUI(3, 2)
    root.toggle_unicode_borders()
    root.enable_logging(logging_level=logging.DEBUG)
    frame = NewUserRegistration(root)
    root.start()


if __name__ == "__main__":
    start_registration()
