"""
# TODO: should place some nice text here...

This module is responsible for creating and managing
Authentification TUI used for checking user's face and 
master password.

...

"""

import logging
import threading

import py_cui

from twopasswords.utils.emailer import Emailer
from twopasswords.config.config import load_config
from twopasswords.utils.database import DatabaseEngine
from twopasswords.utils.face_scanner import FaceScanner
from twopasswords import views_handler

# load configuration
file_paths, email_settings = load_config()


class AuthenticationView:
    """
    A class used to creating and managing
    Authentification TUI that is used for
    checking user's face and master password.

    Attributes
    ----------
    root : py_cui.PyCUI
        Instance of a base PyCUI main interface class
    auth_menu : root.add_scroll_menu
        Adds new scroll menu to a root grid.
        Without this menu added popup functions
        did not work due to some pycui issues...
    attempts : int
        Managing login try attempts.
        At init it equals 4, then substracts 1
        after each unseccessful login attempt.
    database : DatabaseEngine
        Creates DatabaseEngine instance
        for checking the master password entered.

    Methods
    -------
    check_attempts
        Checks login try attempts and stops
        program if there's no attempts left.
    show_facescan_popup
        Shows 'Scanning your face' popup
        and runs scan_face method as a parallel thread.
    scan_face
        Creates FaceScan class instance and
        checking user's face.
    quit_from_facescan(try_again)
        Stops scan_face or restarts one
        if try_again = True.
    show_enter_pragma_box
        Shows enter master password input box
        if FaceScan Auth passed successfully.
    check_pragma
        Checks master password by connecting
        to a Database. If operation was successful,
        switches to a main TwoPasswords TUI.
    rage_quit
        Immediately stops Auth TUI and sends last
        taken face picture as attachment to an email.

    """

    def __init__(self, root: py_cui.PyCUI):
        """
        Sets attempts attribute equal to 4.
        Runs check_attempts and show_facescan_popup
        methods on program start.

        Parameters
        ----------
        root : py_cui.PyCUI
            Instance of a base PyCUI main interface class
        auth_menu : root.add_scroll_menu
            Adds new scroll menu to a root grid.
            Without this menu added popup functions
            did not work due to some pycui issues...
        attempts : int
            Managing login try attempts.
            At init it equals 4, then substracts 1
            after each unseccessful login attempt.

        """

        self.root = root
        self.create_ui_content()
        self.attempts: int = 4
        self.check_attempts()
        self.show_scan_face_popup()

    def create_ui_content(self):
        self.auth_menu = self.root.add_scroll_menu(
            "Authentication", 0, 0, 3, 3, padx=20, pady=3
        )
        self.auth_menu.set_selectable(False)

    def check_attempts(self):
        """
        Checks login try attempts and stops
        program if there's no attempts left.
        Also updates auth_menu with attempts
        left counter.

        """

        self.attempts -= 1

        if self.attempts < 1:
            self.root.stop()
            self.rage_quit()

        else:
            self.auth_menu.clear()
            list_of_text = [""] * 25 + [f"Attempts left: {self.attempts}"]
            self.auth_menu.add_item_list(list_of_text)

    def show_scan_face_popup(self) -> None:
        """
        Shows 'Scanning your face' popup
        and runs scan_face method as a parallel thread.
        Background scan_face thread usage is due to PyCUI
        loading icon popup implementation.

        """

        self.root.show_loading_icon_popup("Please Wait", "Scanning your face")
        self.operation_thread = threading.Thread(target=self.scan_face)
        self.operation_thread.start()

    def scan_face(self) -> None:
        """
        Creates FaceScan class instance and
        checks user's face.
        If auth passed successfully,
        continues to master password check.
        Else asks to try again or quits program.

        """

        # dict with FaceScan results meanings
        result_status = {
            -1: "Stranger's face detected",
            0: "No face detected",
            1: "Auth OK",
            2: "Multiple faces detected",
        }
        result: int = FaceScanner(
            file_paths["user_image"], file_paths["last_image"]
        ).auth()
        self.root.stop_loading_popup()

        # auth succeed, continue to password check
        if result == 1:
            self.show_enter_pragma_box()

        # no or multiple faces was detected
        elif result in (0, 2):
            self.check_attempts()
            self.root.show_yes_no_popup(
                f"{result_status[result]}. Try again?", self.quit_from_facescan
            )

        # stranger's face detected
        elif result == -1:
            self.root.stop()

    def quit_from_facescan(self, try_again):
        """
        Stops scan_face or restarts one
        if try_again = True.

        Parameters
        ----------
        try_again : bool
            To try FaceScan again or quit program

        """

        if try_again:
            self.show_scan_face_popup()
        else:
            self.root.stop()

    def show_enter_pragma_box(self):
        """
        Shows enter master password input box
        if FaceScan Auth passed successfully.
        Runs check_pragma with entered master password.
        Password is hidden by default.

        """

        self.root.show_text_box_popup(
            "Please enter your master password", self.check_pragma, password=True
        )

    def check_pragma(self, pragma):
        """
        Checks master password by creating
        DatabaseEngine instance and trying
        to get all accounts list as a test.
        If operation was successful,
        stops current root PyCUI instance and
        switches to a main TwoPasswords TUI.

        Parameters
        ----------
        pragma : str
            The master password for a Database
            entered in show_enter_pragma_box popup.

        """

        self.database = DatabaseEngine(file_paths["db_path"], pragma)

        try:
            self.database.get_all_accounts()
            self.root.forget_widget(self.auth_menu)
            self.root.stop()
            views_handler.VIEWS_HANDLER.open_view_main(pragma)
            # views_handler.VIEWS_HANDLER.from_auth_to_main(pragma)
        except:
            self.check_attempts()
            self.show_enter_pragma_box()

    def rage_quit(self):
        """
        Sends email report with last taken face
        picture as attachment and Immediately stops
        Authentification TUI.

        """

        # emailer.send_auth_report(
        #     "Warning! Three attempts of Auth failed. Check the image in attachments."
        # )
        self.root.stop()
