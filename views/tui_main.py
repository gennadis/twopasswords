import os
import json
import logging
import datetime
import webbrowser


import py_cui
import pyperclip


from config import config_loader
from utils.database import Account, DatabaseEngine
from utils.password_generator import PasswordGenerator


file_paths, email_settings = config_loader.load()


class TwoPasswordsTUI:
    def __init__(self, root: py_cui.PyCUI, pragma: str):
        self.root = root
        self.database = DatabaseEngine(file_paths["db_path"], pragma)

        self.root.set_title(f"TwoPasswords")

        # Keybindings when in overview mode
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
            "created:",
            py_cui.CYAN_ON_BLACK,
            "startswith",
            match_type="region",
            region=[0, 8],
            include_whitespace=True,
        )
        self.account_card_block.add_text_color_rule(
            "last modified:",
            py_cui.CYAN_ON_BLACK,
            "startswith",
            match_type="region",
            region=[0, 14],
            include_whitespace=True,
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
        self.read_database()

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
        self.account_card_block.set_title("2passwords")
        return logo

    ################ MAIN MENU ################
    def show_menu(self) -> None:
        """
        Displays popup menu with supported commands
        """
        options_list = [
            "Help",
            "Fill database with fakes",
            "CLEAR DATABASE",
            "Import JSON",
            "Export JSON",
            "--Remove database and user picture files--",
        ]
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
        elif option == "Import JSON":
            self.show_import_popup()
        elif option == "Export JSON":
            self.show_export_popup()
        elif option == "--Remove database and user picture files--":
            self.show_remove_database_popup()

    ################ IMPORT JSON ################
    def show_import_popup(self):
        self.root.show_filedialog_popup(
            popup_type="openfile",
            initial_dir=".",
            callback=self.import_json,
            ascii_icons=True,
            limit_extensions=[".json"],
        )

    def import_json(self, filename):
        with open(filename, "r") as open_file:
            content = json.load(open_file)

        for element in content:
            account = Account(
                item=element.get("item"),
                url=element.get("url"),
                username=element.get("username"),
                password=element.get("password"),
                notes=element.get("notes"),
                date_created=element.get("date_created"),
                date_modified=element.get("date_modified"),
            )
            self.database.add_account(account)

        self.root.show_message_popup(
            "Import Done!", f"{len(content)} items were imported from {filename}.json"
        )
        self.read_database()

    ################ EXPORT JSON ################
    def show_export_popup(self):
        self.root.show_filedialog_popup(
            popup_type="saveas",
            callback=self.export_json,
            initial_dir=".",
            ascii_icons=True,
            limit_extensions=[".json"],
        )

    def export_json(self, filename):
        out = []
        accounts = self.database.get_all_accounts()
        for account in accounts:
            out.append(
                {
                    "item": account.item,
                    "url": account.url,
                    "username": account.username,
                    "password": account.password,
                    "notes": account.notes,
                    "date_created": account.date_created,
                    "date_modified": account.date_modified,
                }
            )

        export_data = json.dumps(out)
        with open(filename, "w") as save_file:
            save_file.write(export_data)

        self.root.show_message_popup(
            "Export Done!", f"{len(accounts)} items were exported to {filename}.json"
        )
        self.read_database()

    ################ HANDLE ARROW KEY PRESSES IN ALL ACCOUNTS MENU ################
    def handle_all_accounts_menu_arrows(self, item):
        current_account = self.database.get_exact_account(item)
        self.populate_account_card(current_account)

    ################ Clear database ################
    def show_clear_database_popup(self):
        self.root.show_yes_no_popup("ARE YOU SURE ?!", self.clear_database)

    def clear_database(self, to_clear):
        if to_clear:
            self.database.clear_database()
            self.root.show_message_popup("Done!", f"Database was cleared")
            self.read_database()
            self.account_card_block.clear()
            self.account_card_block.add_item_list(self.get_logo())

    ################ Clear database ################
    def show_remove_database_popup(self):
        self.root.show_yes_no_popup("ARE YOU SURE ?!", self.remove_database)

    def remove_database(self, to_remove):
        if to_remove:
            os.remove(file_paths["db_path"])
            os.remove(file_paths["user_image"])
            self.root.stop()

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
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        self.database.add_account(new_account)
        self.read_database(preserve_selected=True)
        self.populate_account_card(new_account)

        new_account_idx = self.all_accounts_menu.get_item_list().index(new_account.item)
        self.all_accounts_menu.set_selected_item_index(new_account_idx)

        self.root.show_message_popup(
            "Done", f"Account for {new_account.url} added successfully."
        )
        self.root.move_focus(self.account_card_block)

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
        date_format = account.date_created
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
            f"created: {self.format_date(account.date_created)}",
            f"last modified: {self.format_date(account.date_modified)}",
        ]
        if reveal_password:
            structure[4] = account.password  # populate card with password revealed

        self.account_card_block.add_item_list(structure)

    @staticmethod
    def format_date(datetime_string: str):
        datetime_object = datetime.datetime.strptime(
            datetime_string, "%Y-%m-%d %H:%M:%S"
        )
        new_datetime_object = datetime.datetime.strftime(
            datetime_object, "%d %b %Y at %H:%M"
        )

        return new_datetime_object

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
                account.item for account in self.database.get_all_accounts()
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
        # os.system("clear")
        print("HAVE A NICE DAY! 😊")

    ################ SHOW HELP TEXT ################
    def show_help(self):
        help_text = (
            "ENTER HELP TEXT HERE..."
            + "ENTER HELP TEXT HERE..."
            + "ENTER HELP TEXT HERE..."
        )
        self.root.show_message_popup("HELP", help_text)


def start_tui(pragma):
    root = py_cui.PyCUI(8, 8)
    # root.enable_logging(logging_level=logging.DEBUG)
    root.toggle_unicode_borders()
    frame = TwoPasswordsTUI(root, pragma)

    root.start()


if __name__ == "__main__":
    start_tui()
