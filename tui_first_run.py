import os.path
import py_cui
import logging
from time import sleep

from py_cui.colors import CYAN_ON_WHITE, RED_ON_BLACK, WHITE_ON_BLACK
from facescan import FaceScan
from database import create_db

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
        self.populate_welcome_text()
        ################ TAKE PICTURE BUTTON ################
        self.take_picture_button = self.root.add_button(
            "STEP 1 -- Register your face", 0, 1, command=self.take_new_user_picture
        )
        self.take_picture_button.set_color(WHITE_ON_BLACK)

        ################ CREATE DATABASE BUTTON ################
        self.create_database_button = self.root.add_button(
            "STEP 2 -- Create new Database",
            1,
            1,
            command=self.show_create_database_popup,
        )
        self.create_database_button.set_color(WHITE_ON_BLACK)

        ################ EXIT BUTTON ################
        self.exit_button = self.root.add_button("EXIT", 2, 1, command=self.root.stop)
        self.exit_button.set_color(RED_ON_BLACK)

    def populate_welcome_text(self):
        self.welcome_block.clear()
        self.welcome_block.add_item_list(self.welcome_text)

    def take_new_user_picture(self):
        FaceScan("", "user_face.jpg").take_picture()
        sleep(1)
        self.root.show_message_popup("Done!", "Face registered successfully")

        self.welcome_text[2] = "DONE --> 1. Register your face for FaceAuth"
        self.populate_welcome_text()

    def show_create_database_popup(self):
        entry_fields = ["New Password", "Confirm new password"]
        self.root.show_form_popup(
            "Enter your Master password",
            entry_fields,
            entry_fields,
            entry_fields,
            self.check_new_pragma,
        )

    def check_new_pragma(self, form_output):
        """
        form_output is a dictionary,
        hence the ugly implementation with different keys
        """
        if form_output["New Password"] == form_output["Confirm new password"]:
            self.root.show_message_popup(
                "OK!",
                f'{form_output["New Password"]}, {form_output["Confirm new password"]}',
            )
            create_db(database_path, form_output["New Password"], to_create=True)

            self.welcome_text[
                3
            ] = "DONE --> 2. Create new Database with secure master password"
            self.populate_welcome_text()

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
