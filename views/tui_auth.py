import logging
import threading

import py_cui

from config import config_loader
from utils import emailer
from views import tui_main
from utils.database import DatabaseEngine
from utils.facescan import FaceScan


file_paths, email_settings = config_loader.load()


class AuthTUI:
    def __init__(self, root: py_cui.PyCUI):
        self.root = root
        self.root.set_title(f"TwoPasswords")
        self.auth_menu = self.root.add_scroll_menu(
            "Authentication", 0, 0, 3, 3, padx=20, pady=3
        )
        self.auth_menu.set_selectable(False)

        self.attempts = 4
        self.check_attempts()

        self.show_facescan_popup()

    def check_attempts(self):
        self.attempts -= 1

        if self.attempts < 1:
            self.root.stop()
            self.rage_quit()

        else:
            self.auth_menu.clear()
            list_of_text = [""] * 27 + [f"Attempts left: {self.attempts}"]
            self.auth_menu.add_item_list(list_of_text)

    def show_facescan_popup(self) -> None:
        self.root.show_loading_icon_popup("Please Wait", "Scanning your face")
        self.operation_thread = threading.Thread(target=self.scan_face)
        self.operation_thread.start()

    def scan_face(self) -> None:
        result_status = {
            -1: "Stranger's face detected",
            0: "No face detected",
            1: "Auth OK",
            2: "Multiple faces detected",
        }
        result: int = FaceScan(
            file_paths["user_image"], file_paths["last_image"]
        ).auth()
        self.root.stop_loading_popup()

        if result == 1:  # auth succeed, continue to pragma check
            self.show_enter_pragma_box()

        elif result in (0, 2):
            self.check_attempts()

            self.root.show_yes_no_popup(
                f"{result_status[result]}. Try again?", self.quit_from_facescan
            )

        elif result == -1:
            self.root.stop()

    def quit_from_facescan(self, try_again):
        if try_again:
            self.show_facescan_popup()
        else:
            self.root.stop()

    def show_enter_pragma_box(self):
        self.root.show_text_box_popup(
            "Please enter your master password", self.check_pragma, password=True
        )

    def check_pragma(self, pragma):
        self.database = DatabaseEngine(file_paths["db_path"], pragma)
        try:
            self.database.get_all_accounts()
            self.root.forget_widget(self.auth_menu)
            self.root.stop()
            tui_main.start_tui(pragma)

        except:
            self.check_attempts()

            self.show_enter_pragma_box()

    def rage_quit(self):
        emailer.send_auth_report(
            "Warning! Three attempts of Auth failed. Check the image in attachments."
        )
        self.root.stop()


def start_auth():
    root = py_cui.PyCUI(3, 3)
    # root.enable_logging(logging_level=logging.DEBUG)
    root.toggle_unicode_borders()
    frame = AuthTUI(root)

    root.start()


if __name__ == "__main__":
    start_auth()
