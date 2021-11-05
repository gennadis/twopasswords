import os
import sys
import py_cui
import dotenv
import threading
from facescan import FaceScan
from tui import TwoPasswordsApp, start_tui
from ui import ui_push, ui_pop


dotenv.load_dotenv()
DB_PATH = os.environ.get("DB_PATH")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
new_picture = os.environ.get("LAST_IMAGE_PATH")
user_picture = os.environ.get("USER_FACE")


class AuthScreen:
    def __init__(self, ui: py_cui.PyCUI):
        self.ui = ui
        self.root = ui.create_new_widget_set(8, 8)

        self.thread = None

    def apply(self):
        self.ui._in_focused_mode = True
        self.ui.show_loading_icon_popup("Please wait", "Scanning your face... ")

        self.thread = threading.Thread(target=self.scan_face)
        self.thread.start()

    def scan_face(self):
        result_status = {
            -1: "Stranger's face detected",
            0: "No face detected",
            1: "Auth OK",
            2: "Multiple faces detected",
        }
        result: int = FaceScan(user_picture, new_picture).auth()

        if result == 1:  # auth succeed, continue to pragma check
            self.ui.stop_loading_popup()
            self.ui.show_warning_popup("12", "test")

            # ui_push(self.ui, PragmaScreen(self.ui))

    #     elif result in (0, 2):
    #         self.ui.show_yes_no_popup(
    #             f"{result_status[result]}. Try again?", self.quit_from_facescan
    #         )

    #     else:  # result == -1
    #         sys.exit(result_status[result])

    # def quit_from_facescan(self, to_quit):
    #     if to_quit:  # if don't quit
    #         self.show_facescan_popup()
    #     else:
    #         sys.exit()


class PragmaScreen:
    def __init__(self, ui: py_cui.py_cui.PyCUI):
        self.ui = ui
        # self.root = ui.create_new_widget_set(3, 3)

    def apply(self):
        self.ui.show_text_box_popup(
            "Please enter a pragma key", self.check_pragma, password=True
        )

    def check_pragma(self, pragma):
        if pragma == DB_PASSWORD:
            ui_push(self.ui, TwoPasswordsApp(self.ui))

    #     else:
    #         self.apply()


class MultiWindowAuth:
    def __init__(self, root: py_cui.PyCUI):

        # Root PyCUI window
        self.root = root

        # Collect current CUI configuration as a widget set object
        self.widget_set_A = self.root.create_new_widget_set(3, 3)

        # Add a button the the CUI
        self.widget_set_A.add_button("Open 2nd Window", 1, 1, command=self.open_set_B)

        # apply the initial widget set
        self.root.apply_widget_set(self.widget_set_A)

        # Create a second widget set (window). This one will have a 5x5 grid, not 3x3 like the original CUI
        self.widget_set_B = self.root.create_new_widget_set(5, 5)

        # Add a text box to the second widget set
        self.text_box_B = self.widget_set_B.add_text_box(
            "Enter something", 0, 0, column_span=2
        )
        self.text_box_B.add_key_command(py_cui.keys.KEY_ENTER, self.open_set_A)

    def open_set_A(self):
        # Fired on the ENTER key in the textbox. Use apply_widget_set to switch between "windows"
        self.root.apply_widget_set(self.widget_set_A)

    def open_set_B(self):
        # Fired on button press. Use apply_widget_set to switch between "windows"
        self.root.apply_widget_set(self.widget_set_B)


# Create CUI object, pass to wrapper class, and start the CUI
root = py_cui.PyCUI(3, 3)
wrapper = MultiWindowDemo(root)
root.start()
