"""
# TODO: should place some nice text here...

This module is responsible for main TwoPasswords app.
...

"""

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

# load configuration
file_paths, email_settings = config_loader.load()


class TwoPasswordsTUI:
    """
    A class used to create main TwoPasswords TUI.

    Attributes
    ----------
    root : py_cui.PyCUI
        Instance of a base PyCUI main interface class
    database : DatabaseEngine
        Creates DatabaseEngine instance
    all_accounts_menu
        Creates scroll menu on the left side
        for listing all accounts that are stored
        in a Database
    account_card_block
        Creates single account block on the right side
        for showing account credentials
    search_textbox
        Creates search text box on the lower left side
        for searching an account in a Database

    """

    def __init__(self, root: py_cui.PyCUI, pragma: str):
        """
        Parameters
        ----------
        root : py_cui.PyCUI
            Instance of a base PyCUI main interface class
        database : DatabaseEngine
            Creates DatabaseEngine instance
        all_accounts_menu
            Creates scroll menu on the left side
            for listing all accounts that are stored
            in a Database
        account_card_block
            Creates single account block on the right side
            for showing account credentials
        search_textbox
            Creates search text box on the lower left side
            for searching an account in a Database

        """

        self.root = root
        self.database = DatabaseEngine(file_paths["db_path"], pragma)

        self.root.set_title(f"TwoPasswords")
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

        # Mamma mia!
        # Updates account_card_block on all_accounts_menu scrolling
        self.all_accounts_menu.set_on_selection_change_event(
            on_selection_change_event=self.handle_all_accounts_menu_arrows
        )

        self.all_accounts_menu.set_help_text(
            "|  (o)pen website |  (a)dd  |  Arrows - scroll, Esc - exit"
        )

        ################ ACCOUNT CARD BLOCK ################
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

        # On TUI start:
        # Initialize menus with database state
        self.read_database()

    ################ LOGO ################
    def get_logo(self) -> list:
        """
        Prints ascii logo in account_card_block menu
        Note: must be a list

        Returns
        -------
        list
            List of strings with ascii logo parts

        """

        logo: list = [
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
        Shows menu popup with supported commands,
        such as Import, Export, Clear database, etc.

        """

        options_list: list = [
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
        Fires command accordingly to selected option

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
        """
        Shows import JSON file dialog popup
        and passes option to a callback function.

        """

        self.root.show_filedialog_popup(
            popup_type="openfile",
            initial_dir=".",
            callback=self.import_json,
            ascii_icons=True,
            limit_extensions=[".json"],
        )

    def import_json(self, filename):
        """
        Import selected in show_import_popup
        JSON file with a path = filename to a Database

        Parameters
        ----------
        filename : str
        Path to a selected JSON file

        """

        with open(filename, "r") as open_file:
            content: dict = json.load(open_file)

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
            "Import Done!", f"{len(content)} items were imported"
        )
        self.read_database()

    ################ EXPORT JSON ################
    def show_export_popup(self):
        """
        Shows import JSON file dialog popup

        """

        self.root.show_filedialog_popup(
            popup_type="saveas",
            callback=self.export_json,
            initial_dir=".",
            ascii_icons=True,
            limit_extensions=[".json"],
        )

    def export_json(self, filename):
        """
        Export selected in show_export_popup
        JSON file with a path = filename from a Database

        Parameters
        ----------
        filename : str
        Path to a selected JSON file

        """

        out: list = []
        accounts: list[Account] = self.database.get_all_accounts()
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

        export_data: dict = json.dumps(out)
        with open(filename, "w") as save_file:
            save_file.write(export_data)

        self.root.show_message_popup(
            "Export Done!", f"{len(accounts)} items were exported"
        )
        self.read_database()

    ################ HANDLE ARROW KEY PRESSES IN ALL ACCOUNTS MENU ################
    def handle_all_accounts_menu_arrows(self, item):
        """
        Handle all_accounts_menu scrolling
        and fill account_card_block on selection change with item.
        Works with set_on_selection_change_event method.

        Parameters
        ----------
        item : str
            Account's Item (description) selected

        """

        current_account: Account = self.database.get_exact_account(item)
        self.populate_account_card(current_account)

    ################ Clear database ################
    def show_clear_database_popup(self):
        """
        Shows Yes / No popup for clearing a Database

        """
        self.root.show_yes_no_popup("ARE YOU SURE ?!", self.clear_database)

    def clear_database(self, to_clear):
        """
        Clears database entirely if to_clear = True

        Parameters
        ----------
        to_clear : bool
            To clear or not to clear

        """

        if to_clear:
            self.database.clear_database()
            self.root.show_message_popup("Done!", f"Database was cleared")
            self.read_database()
            self.account_card_block.clear()
            self.account_card_block.add_item_list(self.get_logo())

    ################ REMOVE database and user picture ################
    def show_remove_database_popup(self):
        """
        Shows Yes / No popup for deleting* a Database
        *Note: also deletes user picture file

        """

        self.root.show_yes_no_popup("ARE YOU SURE ?!", self.remove_database)

    def remove_database(self, to_remove):
        """
        Deletes database AND user pictire files if to_remove = True

        Parameters
        ----------
        to_remove: bool
            To remove or not to remove

        """

        if to_remove:
            os.remove(file_paths["db_path"])
            os.remove(file_paths["user_image"])
            self.root.stop()

    ################ Fill database with Fakes! ################
    def show_fill_fakes_popup(self):
        """
        Shows fill database with fakes popup
        Asks for number of fakes to fill in (int)

        """

        self.root.show_text_box_popup("How many fakes do you want?", self.fill_fakes)

    def fill_fakes(self, number: str):
        """
        Fills database with int(number) fake accounts
        created by Faker module.

        Parameters
        ----------
        number : int
            Number of fake accounts to fill in
        """

        for _ in range(int(number)):
            new_account: Account = Account.from_faker()
            self.database.add_account(new_account)
        self.root.show_message_popup(
            "Done!", f"Database was filled with {number} fake accounts"
        )
        self.read_database()

    ################ ADD FORM ################
    def show_add_form(self):
        """
        Shows add account form and fires callback function
        Passes dict to a callback function

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
        Saves newly created account to a Database

        Parameters
        ----------
        form_output : dict

        """
        if form_output["Password: custom or (x)kcd, (r)andom, (p)in"] == "x":
            new_password: str = PasswordGenerator("xkcd", 4).generate_password()
        elif form_output["Password: custom or (x)kcd, (r)andom, (p)in"] == "r":
            new_password: str = PasswordGenerator("random", 16).generate_password()
        elif form_output["Password: custom or (x)kcd, (r)andom, (p)in"] == "p":
            new_password: str = PasswordGenerator("pin", 4).generate_password()
        else:
            new_password: str = form_output[
                "Password: custom or (x)kcd, (r)andom, (p)in"
            ]

        new_account: Account = Account(
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

        new_account_idx: int = self.all_accounts_menu.get_item_list().index(
            new_account.item
        )
        self.all_accounts_menu.set_selected_item_index(new_account_idx)

        self.root.show_message_popup(
            "Done", f"Account for {new_account.url} added successfully."
        )
        self.root.move_focus(self.account_card_block)

    ################ EDIT FORM ################
    def show_edit_form(self):
        """
        Shows edit account password form and fires callback function
        Passes dict to a callback function
        {field names : entered values}

        """

        self.root.show_text_box_popup(
            "Enter new password: custom or (x)kcd, (r)andom, (p)in",
            self.save_edit_form_results,
        )

    def save_edit_form_results(self, form_output):
        """
        Saves edited account password to a Database
        and modifies account.last_modified value.

        Parameters
        ----------
        form_output : string

        """

        current_line: str = self.all_accounts_menu.get()
        current_account: Account = self.database.get_account(current_line)

        if form_output == "x":
            new_password: str = PasswordGenerator("xkcd", 4).generate_password()
        elif form_output == "r":
            new_password: str = PasswordGenerator("random", 16).generate_password()
        elif form_output == "p":
            new_password: str = PasswordGenerator("pin", 4).generate_password()
        else:
            new_password: str = form_output

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
        Show Yes / No delete account popup
        Passes bool to a callback function

        """

        self.root.show_yes_no_popup(
            "Are you sure you want to delete this account? ",
            self.save_delete_form_results,
        )

    def save_delete_form_results(self, to_delete: bool):
        """
        Saves changes to a Database if to_delete = True

        Parameters
        ----------
        to_delete : bool

        """

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
        """
        Populates all accounts scroll menu with accounts

        Parameters
        ----------
        accounts : list
            List of account to fill in

        """

        self.all_accounts_menu.clear()
        self.all_accounts_menu.add_item_list(accounts)
        self.all_accounts_menu.set_title(
            f"All accounts: {len(self.all_accounts_menu.get_item_list())} items"
        )

    def populate_account_card(self, account: Account, reveal_password: bool = False):
        """
        Populates account_card_block menu with account credentials

        Parameters
        ----------
        account : Account
            Account which will be filled in accoun_card_block
        reveal_password : bool
            Whether to reveal passwords in accoun_card_block or not
            (default is False)

        """

        self.account_card_block.clear()
        self.account_card_block.set_title(account.item)
        structure: list = [
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
        """
        Formats dates in account_card_block menu
        from '2021-12-21 10:01:20' to '21 Dec 2021 10:01'

        Parameters
        ----------
        datetime_string : str
            Date as a string that should be formatted

        Returns
        -------
        new_datetime_object : str
            Date in a '21 Dec 2021 10:01' format

        """

        datetime_object: str = datetime.datetime.strptime(
            datetime_string, "%Y-%m-%d %H:%M:%S"
        )
        new_datetime_object: str = datetime.datetime.strftime(
            datetime_object, "%d %b %Y at %H:%M"
        )

        return new_datetime_object

    ################ SEARCH FUNCTION ################
    def search_account_card(self) -> None:
        """
        Searches Database for account

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
            account_idx: int = self.all_accounts_menu.get_item_list().index(result.item)
            self.all_accounts_menu.set_selected_item_index(account_idx)

        except:
            self.root.show_warning_popup(
                "Search error", "Unable to get such account from database"
            )
        self.search_textbox.clear()

    ################ PREVIEW CARD ################
    def preview_account_card(self):
        """
        Fill account_card_block with account information

        """

        current_account: str = self.all_accounts_menu.get()
        account_info: Account = self.database.get_account(current_account)
        self.populate_account_card(account_info)

    ################ OPEN CARD ################
    def open_account_card(self):
        """
        Opens account in account_card_block menu
        and moves focus to account menu

        """

        current_account: str = self.all_accounts_menu.get()
        account_info: Account = self.database.get_account(current_account)
        self.populate_account_card(account_info)
        self.root.move_focus(self.account_card_block)

    ################ COPY TO CLIPBOARD ################
    def copy_password(self):
        """
        Copies password to a clipboard
        Powered by pyperclip

        """

        account_title: str = self.account_card_block.get_title()
        account: Account = self.database.get_account(account_title)
        pyperclip.copy(account.password)

    ################ REVEAL PASSWORD ################
    def reveal_password(self):
        """
        Reveals password in account_card_block

        """

        account_title: str = self.account_card_block.get_title()
        account: Account = self.database.get_account(account_title)
        self.populate_account_card(account, reveal_password=True)

    ################ OPEN WEBBROWSER ################
    def open_website(self):
        """
        Opens a website in a default browser.
        Copies password to a clipboard.

        """

        account_title: str = self.all_accounts_menu.get()
        account: Account = self.database.get_account(account_title)
        pyperclip.copy(account.password)
        webbrowser.open(account.url)

    ################ SWITCH WIDGETS ################
    def switch_widget(self):
        """
        Switches focus on a widgets
        by hitting TAB button.

        """

        widgets_count: int = len(self.root.get_widgets().keys())  # len([0, 1, 2]) == 3
        current_widget_id: int = self.root._selected_widget

        # cycle through all widgets
        if current_widget_id < widgets_count - 1:
            self.root.set_selected_widget(current_widget_id + 1)
        else:
            self.root.set_selected_widget(0)

    ################ LOAD DATABASE ################
    def read_database(self, preserve_selected=False):
        """
        Commits changes to a Database.
        Loads all items from a Database.
        Shows an error if Database is not reachable or broken.

        Parameters
        ----------
        preserve_selected : bool
            To preserve selection in all_accounts_menu

        """

        try:
            selected_account: int = self.all_accounts_menu.get_selected_item_index()
            self.database.safe_push()
            accounts: list = sorted(
                account.item for account in self.database.get_all_accounts()
            )

            self.populate_all_accounts_menu(accounts)

            if preserve_selected:
                self.all_accounts_menu.set_selected_item_index(selected_account)

        except:
            self.root.show_warning_popup(
                "Database Fail",
                "Unable to open database",
            )

    ################ SAY BYE ON EXIT ################
    def say_bye(self):
        """
        Prints some nice text on exit

        """

        print("HAVE A NICE DAY! 😊")

    ################ SHOW HELP TEXT ################
    def show_help(self):
        """
        Shows popup with help info

        """

        help_text: str = "ENTER HELP TEXT HERE..." + " AND HERE..."
        self.root.show_message_popup("HELP", help_text)


def start_tui(pragma):
    """
    Runs TwoPasswords TUI.

    """

    root = py_cui.PyCUI(8, 8)
    # root.enable_logging(logging_level=logging.DEBUG)
    root.toggle_unicode_borders()
    frame = TwoPasswordsTUI(root, pragma)

    root.start()


if __name__ == "__main__":
    start_tui()
