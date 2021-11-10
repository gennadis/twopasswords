import os
import threading
import dotenv
import py_cui
import logging
from utils.facescan import FaceScan
from utils.emailer import EmailSender
from utils.database import DatabaseEngine
from views.tui_main import start_tui

dotenv.load_dotenv()
DB_PATH = os.environ.get("DB_PATH")

LAST_PICTURE = os.environ.get("LAST_IMAGE_PATH")
USER_PICTURE = os.environ.get("USER_FACE")

EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_SERVER = os.environ.get("EMAIL_SERVER")
EMAIL_PORT = os.environ.get("EMAIL_PORT")


class AuthTUI:
    def __init__(self, root: py_cui.PyCUI):
        self.root = root
        self.root.set_title(f"TwoPasswords")
        self.auth_menu = self.root.add_scroll_menu(
            "Authentication", 0, 0, 3, 3, padx=20, pady=3
        )
        self.auth_menu.set_selectable(False)

        self.attempts = 3
        self.show_attempts_left()

        self.show_facescan_popup()

    def show_attempts_left(self):
        self.auth_menu.clear()
        list_of_text = [""] * 25 + [f"Attempts left: {self.attempts}"]
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
        result: int = FaceScan(USER_PICTURE, LAST_PICTURE).auth()
        self.root.stop_loading_popup()

        if result == 1:  # auth succeed, continue to pragma check
            self.show_enter_pragma_box()

        elif result in (0, 2):
            self.attempts -= 1

            if self.attempts < 1:
                self.rage_quit()

            self.show_attempts_left()
            self.root.show_yes_no_popup(
                f"{result_status[result]}. Try again?", self.quit_from_facescan
            )

        elif result == -1:
            self.root.stop()
            # os.system("clear")
            # print("WARNING: Facescan Auth Failed!")
            # os._exit(1)
            # # sys.exit()
            # # self.operation_thread.stop()

    def quit_from_facescan(self, try_again):
        if try_again:
            self.show_facescan_popup()
        else:
            self.root.stop()

    def show_enter_pragma_box(self):
        self.root.show_text_box_popup(
            "Please enter a pragma key", self.check_pragma, password=True
        )

    def check_pragma(self, pragma):
        self.database = DatabaseEngine(DB_PATH, pragma)
        try:
            # self.database.safe_push()
            self.database.get_all_accounts()
            self.root.forget_widget(self.auth_menu)
            self.root.stop()
            start_tui(pragma)

        except:
            self.attempts -= 1

            if self.attempts < 1:
                self.rage_quit()

            self.show_attempts_left()
            self.show_enter_pragma_box()

    def rage_quit(self):
        EmailSender(
            "Face auth report",
            "Warning! Last auth was failed! Check the image in attachments!!!",
            EMAIL_ADDRESS,
            EMAIL_PASSWORD,
            LAST_PICTURE,
            EMAIL_SERVER,
            EMAIL_PORT,
        ).send_email()

        self.root.stop()


def start_auth():
    root = py_cui.PyCUI(3, 3)
    root.enable_logging(logging_level=logging.DEBUG)
    root.toggle_unicode_borders()
    frame = AuthTUI(root)

    root.start()


if __name__ == "__main__":
    start_auth()
