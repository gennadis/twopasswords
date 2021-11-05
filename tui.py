import py_cui
import os
import dotenv
import pyperclip
from database import Account, DatabaseEngine
from password_generator import PasswordGenerator

dotenv.load_dotenv()
DB_PATH = os.environ.get("DB_PATH")
DB_PASSWORD = os.environ.get("DB_PASSWORD")

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

        ################ ALL ACCOUNTS MENU ################
        self.all_accounts_menu = self.root.add_scroll_menu(
            "All Accounts", 0, 0, row_span=7, column_span=2
        )
        self.all_accounts_menu.set_selected_color(py_cui.BLACK_ON_WHITE)

        self.all_accounts_menu.add_key_command(py_cui.keys.KEY_TAB, self.switch_widget)

        self.all_accounts_menu.add_key_command(
            py_cui.keys.KEY_SPACE, self.open_account_card
        )
        self.all_accounts_menu.add_key_command(
            py_cui.keys.KEY_O_LOWER, self.open_account_card
        )
        self.all_accounts_menu.add_key_command(
            py_cui.keys.KEY_A_LOWER, self.show_add_form
        )

        self.all_accounts_menu.set_help_text(
            "|  (o)pen  |  (a)dd  |  Arrows - scroll, Esc - exit"
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
        self.account_card_block.set_help_text(
            "|  (c)opy password  |  (e)dit  |  (d)elete  |  Arrows - scroll, Esc - exit"
        )
        self.account_card_block.add_key_command(py_cui.keys.KEY_TAB, self.switch_widget)
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

        return logo

    ################ MAIN MENU ################
    def show_menu(self) -> None:
        """
        Displays popup menu with supported commands
        """
        options_list = ["Menu option 1", "Menu option 2", "Menu option 3"]
        self.root.show_menu_popup(
            "Main menu",
            options_list,
            self.set_menu_option,
        )

    def set_menu_option(self, option) -> None:
        """
        Manages menu option choices
        """
        if option == "Menu option 1":
            pass
        elif option == "Menu option 2":
            pass
        elif option == "Menu option 3":
            pass

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

    def populate_account_card(self, account: Account) -> None:
        self.account_card_block.clear()
        self.account_card_block.set_title(account.item)

        structure = [
            "",
            "username",
            account.username,
            "password",
            account.password,
            # "**********",
            "",
            "website",
            account.url,
        ]

        self.account_card_block.add_item_list(structure)

    ################ SEARCH FUNCTION ################
    def search_account_card(self) -> None:
        """
        Searches for account card
        """
        search_value: str = self.search_textbox.get()
        if len(search_value) == 0:
            self.root.show_error_popup(
                "Invalid query", "Please enter a valid search query"
            )
            return

        try:
            result: Account = self.database.get_account(search_value)
            self.populate_account_card(result)
            # self.root.move_focus(self.account_card_block)

        except:
            self.root.show_warning_popup(
                "Search error", "Unable to get such account from database"
            )
        self.search_textbox.clear()

    ################ OPEN CARD ################
    def open_account_card(self):
        """
        Opens account card view
        """
        current_account = self.all_accounts_menu.get()
        account_info = self.database.get_account(current_account)
        self.populate_account_card(account_info)
        # self.root.move_focus(self.account_card_block)

    @staticmethod
    def normalize_url(url: str) -> str:
        return url[1].split("//")[1].replace("www.", "")

    ################ COPY TO CLIPBOARD ################
    def copy_password(self):
        # current_line = self.account_card_block.get()
        password = self.account_card_block.get_item_list()[4]
        pyperclip.copy(password)

    ################ SWITCH WIDGETS ################
    def switch_widget(self):
        """
        Cycles through all widgets
        Current count of widgets is *THREE*
        """
        pass
        # widgets_count = len(self.root.get_widgets().keys())  # len([0, 1, 2]) == 3
        # current_widget_id = self.root._selected_widget

        # if current_widget_id < widgets_count - 1:
        #     self.root.set_selected_widget(current_widget_id + 1)
        # else:
        #     self.root.set_selected_widget(0)

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
                "Unable to read database",
            )


root = py_cui.PyCUI(8, 8)
root.toggle_unicode_borders()
frame = TwoPasswordsApp(root)

# Start App
root.start()
