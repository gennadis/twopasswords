import py_cui
import os
import sys
import logging
import dotenv
import pyperclip
import threading
import webbrowser
from datetime import datetime
from facescan import FaceScan
from time import sleep
from database import Account, DatabaseEngine
from password_generator import PasswordGenerator

dotenv.load_dotenv()
DB_PATH = os.environ.get("DB_PATH")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

new_picture = os.environ.get("LAST_IMAGE_PATH")
user_picture = os.environ.get("USER_FACE")


__version__ = "0.7"


class TwoPasswordsApp:
    def __init__(self, root: py_cui.PyCUI):
        self.root = root
        self.database = DatabaseEngine(DB_PATH, DB_PASSWORD)

        # Set title
        self.root.set_title(f"TwoPasswords v{__version__}")

        # Keybindings when in overview mode, and set info bar
        self.root.add_key_command(py_cui.keys.KEY_M_LOWER, self.show_menu)
        self.root.add_key_command(py_cui.keys.KEY_TAB, self.switch_widget)
        self.root.set_status_bar_text("Quit - q | Menu - m ")

        # say bye on exit
        self.root.run_on_exit(self.say_bye)

        ################ ALL ACCOUNTS MENU ################
        self.all_accounts_menu = self.root.add_scroll_menu(
            "All Accounts", 0, 0, row_span=7, column_span=2
        )

        self.all_accounts_menu.set_selected_color(py_cui.BLACK_ON_WHITE)

        self.all_accounts_menu.add_key_command(py_cui.keys.KEY_TAB, self.switch_widget)

        self.all_accounts_menu.add_key_command(
            py_cui.keys.KEY_SPACE, self.preview_account_card
        )
        self.all_accounts_menu.add_key_command(
            py_cui.keys.KEY_ENTER, self.open_account_card
        )
        self.all_accounts_menu.add_key_command(
            py_cui.keys.KEY_O_LOWER, self.open_website
        )
        self.all_accounts_menu.add_key_command(
            py_cui.keys.KEY_A_LOWER, self.show_add_form
        )

        # --------------- MAMMA MIA!!!
        self.all_accounts_menu.set_on_selection_change_event(
            on_selection_change_event=self.handle_all_accounts_menu_arrows
        )
        # --------------- MAMMA MIA!!!

        self.all_accounts_menu.set_help_text(
            "|  (o)pen website |  (a)dd  |  Arrows - scroll, Esc - exit"
        )

        ################ ACCOUNT CARD MENU ################
        self.account_card_block = self.root.add_scroll_menu(
            "Account card", 0, 2, row_span=8, column_span=6
        )
        self.account_card_block.add_item_list(self.get_logo())  # add logo on app start

        self.account_card_block.add_text_color_rule(
            "username", py_cui.CYAN_ON_BLACK, "startswith"
        )
        self.account_card_block.add_text_color_rule(
            "password", py_cui.CYAN_ON_BLACK, "startswith"
        )
        self.account_card_block.add_text_color_rule(
            "website", py_cui.CYAN_ON_BLACK, "startswith"
        )
        self.account_card_block.add_text_color_rule(
            "notes", py_cui.CYAN_ON_BLACK, "startswith"
        )
        self.account_card_block.add_text_color_rule(
            "created", py_cui.CYAN_ON_BLACK, "startswith"
        )
        self.account_card_block.add_text_color_rule(
            "modified", py_cui.CYAN_ON_BLACK, "startswith"
        )

        self.account_card_block.set_help_text(
            "|  (r)eveal password |  (c)opy password  |  (e)dit  |  (d)elete  |  Arrows - scroll, Esc - exit"
        )
        self.account_card_block.add_key_command(py_cui.keys.KEY_TAB, self.switch_widget)
        self.account_card_block.add_key_command(
            py_cui.keys.KEY_R_LOWER, self.reveal_password
        )
        self.account_card_block.add_key_command(
            py_cui.keys.KEY_C_LOWER, self.copy_password
        )
        self.account_card_block.add_key_command(
            py_cui.keys.KEY_E_LOWER, self.show_edit_form
        )

        self.account_card_block.add_key_command(
            py_cui.keys.KEY_D_LOWER, self.show_delete_form
        )

        ################ SEARCH MENU ################
        self.search_textbox = self.root.add_text_box(
            "Search TwoPasswords", 7, 0, column_span=2
        )
        self.search_textbox.set_border_color(py_cui.CYAN_ON_BLACK)
        self.search_textbox.add_key_command(py_cui.keys.KEY_TAB, self.switch_widget)
        self.search_textbox.add_key_command(
            py_cui.keys.KEY_ENTER, self.search_account_card
        )
        self.search_textbox.set_help_text("Enter your search query, Esc - exit")

        ################ INITIALIZE MENUS WITH DATABASE STATUS ################
        self.show_facescan_popup()
        # self.read_database()
        # self.show_enter_pragma_box()

    ################ INITIALIZE AUTH PROCESS ################

    def show_facescan_popup(self) -> None:
        self.root.show_loading_icon_popup("Please Wait", "Scanning your face...")
        self.operation_thread = threading.Thread(target=self.scan_face)
        self.operation_thread.start()

    def scan_face(self) -> None:
        result_status = {
            -1: "Stranger's face detected",
            0: "No face detected",
            1: "Auth OK",
            2: "Multiple faces detected",
        }
        result: int = FaceScan(user_picture, new_picture).auth()
        self.root.stop_loading_popup()

        if result == 1:  # auth succeed, continue to pragma check
            self.show_enter_pragma_box()

        elif result in (0, 2):
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
        if pragma == DB_PASSWORD:
            self.read_database()
        else:
            self.show_enter_pragma_box()

    ################ LOGO ################
    def get_logo(self) -> list:
        """
        Gets ascii app logo as a list of strings
        Logo must be a list because self.account_card_block takes only a lists
        """
        logo = [
            "  ......   .........    ......   ",
            " ::::::::  :::::::::   ::::::::  ",
            ":+:    :+: :+:    :+: :+:    :+: ",
            "      +:+  +:+    +:+ +:+        ",
            "    +#+    +#++:++#+  +#++:++#++ ",
            "  +#+      +#+               +#+ ",
            " #+#       #+#        #+#    #+# ",
            "########## ###         ########  ",
            "2passwords ###          ######   ",
        ]

        return logo

    ################ MAIN MENU ################
    def show_menu(self) -> None:
        """
        Displays popup menu with supported commands
        """
        options_list = ["Help", "Fill database with fakes", "CLEAR DATABASE"]
        self.root.show_menu_popup(
            "Main menu",
            options_list,
            self.set_menu_option,
        )

    def set_menu_option(self, option) -> None:
        """
        Manages menu option choices
        """
        if option == "Help":
            self.show_help()
        elif option == "Fill database with fakes":
            self.show_fill_fakes_popup()
        elif option == "CLEAR DATABASE":
            self.show_clear_database_popup()

    ################ HANDLE ARROW KEY PRESSES IN ALL ACCOUNTS MENU ################
    def handle_all_accounts_menu_arrows(self, item):
        current_account = self.database.get_exact_account(item)
        self.populate_account_card(current_account)

    ################ Fill database with Fakes! ################
    def show_clear_database_popup(self):
        self.root.show_yes_no_popup("ARE YOU SURE ?!", self.clear_database)

    def clear_database(self, to_clear):
        if to_clear:
            self.database.clear_database()
            self.root.show_message_popup("Done!", f"Database was cleared")
            self.read_database()

        else:
            self.root.show_message_popup("Database clear was cancelled")

    ################ Fill database with Fakes! ################
    def show_fill_fakes_popup(self):
        self.root.show_text_box_popup("How many fakes do you want?", self.fill_fakes)

    def fill_fakes(self, number: str):
        for i in range(int(number)):
            new_account = Account.from_faker()
            self.database.add_account(new_account)
        self.root.show_message_popup(
            "Done!", f"Database was filled with {number} fake accounts"
        )
        self.read_database()

    ################ ADD FORM ################
    def show_add_form(self):
        """
        Passes dict to a callback function
        {field names : entered values}
        """
        self.root.show_form_popup(
            "Add new account",
            [
                "Item name",
                "Website",
                "Username",
                "Password: custom or (x)kcd, (r)andom, (p)in",
                "Notes",
            ],
            # passwd_fields=["Password"],
            required=["Username", "Password"],
            callback=self.save_add_form_results,
        )

    def save_add_form_results(self, form_output):
        """
        form_output is a dictionary,
        hence the ugly implementation with different keys
        """
        if form_output["Password: custom or (x)kcd, (r)andom, (p)in"] == "x":
            new_password = PasswordGenerator("xkcd", 4).generate_password()
        elif form_output["Password: custom or (x)kcd, (r)andom, (p)in"] == "r":
            new_password = PasswordGenerator("random", 16).generate_password()
        elif form_output["Password: custom or (x)kcd, (r)andom, (p)in"] == "p":
            new_password = PasswordGenerator("pin", 4).generate_password()
        else:
            new_password = form_output["Password: custom or (x)kcd, (r)andom, (p)in"]

        new_account = Account(
            form_output["Item name"],
            form_output["Website"],
            form_output["Username"],
            new_password,
            form_output["Notes"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        self.database.add_account(new_account)
        self.read_database(preserve_selected=True)
        self.populate_account_card(new_account)

        self.root.show_message_popup(
            "Done", f"Account for {new_account.url} added successfully."
        )

    ################ EDIT FORM ################
    def show_edit_form(self):
        """
        Passes dict to a callback function
        {field names : entered values}
        """
        self.root.show_text_box_popup(
            "Enter new password: custom or (x)kcd, (r)andom, (p)in",
            self.save_edit_form_results,
        )

    def save_edit_form_results(self, form_output):
        """
        in this case form_output is a string
        """
        current_line: str = self.all_accounts_menu.get()
        current_account: Account = self.database.get_account(current_line)

        if form_output == "x":
            new_password = PasswordGenerator("xkcd", 4).generate_password()
        elif form_output == "r":
            new_password = PasswordGenerator("random", 16).generate_password()
        elif form_output == "p":
            new_password = PasswordGenerator("pin", 4).generate_password()
        else:
            new_password = form_output

        self.database.update_account(current_account, new_password)
        self.read_database(preserve_selected=True)

        updated_account: Account = self.database.get_account(current_line)
        self.populate_account_card(updated_account)

        self.root.show_message_popup(
            "Done", f"Password for {current_account.url} updated successfully."
        )

    ################ DELETE FORM ################
    def show_delete_form(self):
        """
        passes bool to next functions
        """
        self.root.show_yes_no_popup(
            "Are you sure you want to delete this account? ",
            self.save_delete_form_results,
        )

    def save_delete_form_results(self, to_delete: bool):
        if to_delete:
            current_line: str = self.all_accounts_menu.get()
            current_account: Account = self.database.get_account(current_line)
            self.database.delete_account(current_account)

            self.read_database(preserve_selected=True)

            # show logo
            self.account_card_block.clear()
            self.account_card_block.add_item_list(self.get_logo())

            self.root.show_message_popup(
                "Done", f"Account for {current_account.url} deleted successfully."
            )
        else:
            pass

    ################ POPULATION FUNCTIONS ################
    def populate_all_accounts_menu(self, accounts: list) -> None:
        self.all_accounts_menu.clear()
        self.all_accounts_menu.add_item_list(accounts)
        self.all_accounts_menu.set_title(
            f"All accounts: {len(self.all_accounts_menu.get_item_list())} items"
        )

    def populate_account_card(self, account: Account, reveal_password: bool = False):
        self.account_card_block.clear()
        self.account_card_block.set_title(account.item)

        structure = [
            "",
            "username",
            account.username,
            "password",
            "**********",
            "",
            "website",
            account.url,
            "",
            "notes",
            account.notes,
            "",
            "",
            "created",
            account.date_created,
            "modified",
            account.date_modified,
        ]
        if reveal_password:
            structure[4] = account.password  # populate card with password revealed

        self.account_card_block.add_item_list(structure)

    ################ SEARCH FUNCTION ################
    def search_account_card(self) -> None:
        """
        Searches for account card
        """
        search_value: str = self.search_textbox.get()
        if len(search_value) == 0:
            self.root.show_warning_popup(
                "Invalid query", "Please enter a valid search query"
            )
            return

        try:
            result: Account = self.database.get_account(search_value)
            self.populate_account_card(result)
            self.root.move_focus(self.account_card_block)
            # set selection on result in all_accounts_menu
            account_idx = self.all_accounts_menu.get_item_list().index(result.item)
            self.all_accounts_menu.set_selected_item_index(account_idx)

        except:
            self.root.show_warning_popup(
                "Search error", "Unable to get such account from database"
            )
        self.search_textbox.clear()

    ################ PREVIEW CARD ################
    def preview_account_card(self):
        """
        Opens account card view
        """
        current_account = self.all_accounts_menu.get()
        account_info = self.database.get_account(current_account)
        self.populate_account_card(account_info)
        # self.root.move_focus(self.account_card_block)

    ################ OPEN CARD ################
    def open_account_card(self):
        """
        Opens account card view
        """
        current_account = self.all_accounts_menu.get()
        account_info = self.database.get_account(current_account)
        self.populate_account_card(account_info)
        self.root.move_focus(self.account_card_block)

    # @staticmethod
    # def normalize_url(url: str) -> str:
    #     return url[1].split("//")[1].replace("www.", "")

    # ################ COPY TO CLIPBOARD ################
    def copy_password(self):
        account_title = self.account_card_block.get_title()
        account = self.database.get_account(account_title)

        pyperclip.copy(account.password)

    ################ REVEAL PASSWORD ################
    def reveal_password(self):
        account_title = self.account_card_block.get_title()
        account = self.database.get_account(account_title)
        self.populate_account_card(account, reveal_password=True)

    ################ OPEN WEBBROWSER ################
    def open_website(self):
        account_title = self.all_accounts_menu.get()
        account = self.database.get_account(account_title)
        pyperclip.copy(account.password)
        webbrowser.open(account.url)

    ################ SWITCH WIDGETS ################
    def switch_widget(self):
        """
        Cycles through all widgets
        Current count of widgets is *THREE*
        """
        # pass
        widgets_count = len(self.root.get_widgets().keys())  # len([0, 1, 2]) == 3
        current_widget_id = self.root._selected_widget

        if current_widget_id < widgets_count - 1:
            self.root.set_selected_widget(current_widget_id + 1)
        else:
            self.root.set_selected_widget(0)

    ################ LOAD DATABASE ################
    def read_database(self, preserve_selected=False):
        try:
            selected_account: int = self.all_accounts_menu.get_selected_item_index()
            self.database.safe_push()
            accounts = sorted(
                [account[1] for account in self.database.get_all_accounts()]
            )
            self.populate_all_accounts_menu(accounts)

            if preserve_selected:
                # if len(self.all_accounts_menu.get_item_list()) > selected_account:
                self.all_accounts_menu.set_selected_item_index(selected_account)

        except:
            self.root.show_warning_popup(
                "Database Fail",
                "Unable to open database",
            )

    ################ SAY BYE ON EXIT ################
    def say_bye(self):
        os.system("clear")
        print("HAVE A NICE DAY! 😊")

    ################ SHOW HELP TEXT ################
    def show_help(self):
        help_text = (
            "ENTER HELP TEXT HERE..."
            + "ENTER HELP TEXT HERE..."
            + "ENTER HELP TEXT HERE..."
        )
        self.root.show_message_popup("HELP", help_text)


def start_tui():
    root = py_cui.PyCUI(8, 8)
    root.enable_logging(logging_level=logging.DEBUG)
    root.toggle_unicode_borders()
    frame = TwoPasswordsApp(root)

    root.start()


if __name__ == "__main__":
    start_tui()
