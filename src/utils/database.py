"""
# TODO: should place some nice text here...

This module is responsible for Database and it's entries (Accounts) work.
...

"""

from __future__ import annotations
from datetime import datetime

from faker import Faker
from sqlcipher3 import dbapi2 as sqlite3

from utils.password_generator import PasswordGenerator


def create_db(path: str, password: str, to_create: bool = False) -> None:
    """
    Creates a new SQLCipher3 powered database
    for storing user accounts credentials.
    Runs once on new user registration.

    Parameters
    ----------
    path : str
        The path where Database will be stored
    password : str
        The password which will be used to encrypt Database
    to_create : bool, optional
        Whether to create or not (default is False)

    """

    if to_create:
        connection = sqlite3.connect(path)
        if password is not None:
            # set pragma key as a master password
            connection.execute(f"pragma key = {password}")
        cursor = connection.cursor()
        cursor.execute(
            """CREATE TABLE accounts (
            id INTEGER PRIMARY KEY,
            item TEXT,
            url TEXT,
            username TEXT,
            password TEXT,
            notes TEXT,
            date_created TEXT,
            date_modified TEXT
            )"""
        )
        connection.commit()
        connection.close()


class DatabaseEngine:
    """
    A class used to represent a Database connection and
    manage base fucntionality using implemented methods.

    Attributes
    ----------
    path : str
        The path where Database is stored
    password : str
        The master password used for Database encryption

    Methods
    -------
    safe_push
        Commits changes made to a Database
    add_account(account)
        Adds Account to a Database
    get_account(item)
        Gets Account from a Database by Account item (description) name using SQL LIKE statement
    get_exact_account(item)
        Gets Account from a Database by Account item (description) name
    get_all_accounts
        Gets all Accounts from a Database
    update_account(account, password)
        Updates Account's password in a Database
    delete_account
        Deletes Account from a Database
    clear_database
        Wipes Database completely

    """

    def __init__(self, path: str, password: str = None):
        """
        Parameters
        ----------
        path : str
            The path where Database is stored
        password : str
            The master password used for Database encryption

        """

        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()
        if password is not None:
            # set pragma key as a master password
            self.cursor.execute(f"pragma key={password}")

    def safe_push(self) -> None:
        """
        Commits changes made to a Database.

        """

        self.connection.commit()

    def add_account(self, account: Account) -> None:
        """
        Adds Account to a Database.

        Parameters
        ----------
        account : Account
            The account that will be added

        """

        self.cursor.execute(
            "INSERT INTO accounts (item, url, username, password, notes, date_created, date_modified) VALUES (:item, :url, :username, :password, :notes, :date_created, :date_modified)",
            {
                "item": account.item,
                "url": account.url,
                "username": account.username,
                "password": account.password,
                "notes": account.notes,
                "date_created": account.date_created,
                "date_modified": account.date_modified,
            },
        )

    def get_account(self, item: str) -> Account:
        """
        Gets Account from a Database by Account item
        (description) name using SQL LIKE statement.

        Parameters
        ----------
        item : str
            The account item name (description)

        Returns
        -------
        Account
            The Account most similar by item name

        """

        self.cursor.execute(
            "SELECT * FROM accounts WHERE item like '%{0}%'".format(item)
        )
        return Account(*self.cursor.fetchone()[1:])  # [1:] -> without ID

    def get_exact_account(self, item: str) -> Account:
        """
        Gets Account from a Database by Account item
        (description) name - returns exact Account if any.

        Parameters
        ----------
        item : str
            The account item name (description)

        Returns
        -------
        Account
            The exact Account by item name

        """

        self.cursor.execute("SELECT * FROM accounts WHERE item=:item;", {"item": item})
        return Account(*self.cursor.fetchone()[1:])  # [1:] -> without ID

    def get_all_accounts(self) -> list[Account]:
        """
        Gets all Accounts from a Database

        Returns
        -------
        list
            The list of all Accounts stored in a Database

        """

        self.cursor.execute("SELECT * FROM accounts")
        return [Account(*account[1:]) for account in self.cursor.fetchall()]

    def update_account(self, account: Account, password: str) -> None:
        """
        Updates Account's password in a Database and
        sets date_modified attribute value to current time.
        Currently only password value update is implemented.

        Parameters
        ----------
        account : Account
            The Account which password will be updated
        password: str
            The new password for a Account

        """

        self.cursor.execute(
            "UPDATE accounts SET password=:password, date_modified=:date_modified WHERE url=:url AND username=:username",
            {
                "item": account.item,
                "url": account.url,
                "username": account.username,
                "password": password,
                "notes": account.notes,
                "date_created": account.date_created,
                "date_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        )

    def delete_account(self, account: Account) -> None:
        """
        Deletes Account from a Database
        checked by it's url and username.

        Parameters
        ----------
        account : Account
            The Account that will be deleted

        """

        self.cursor.execute(
            "DELETE FROM accounts WHERE url=:url AND username=:username",
            {"url": account.url, "username": account.username},
        )

    def clear_database(self) -> None:
        """
        Wipes Database 'accounts' table completely.

        """

        self.cursor.execute("DELETE FROM accounts")


class Account:
    """
    A class used to represent an Account
    that will be stored in a Database.

    Attributes
    ----------
    item : str
        The item name (description) of an Account
    url : str
        The Account's website URL
    username: str
        The Account's username
    password: str
        The Account's password
    notes: str
        The Account's brief text notes
    date_created: str
        The Account's date of creation
    date_modified: str
        The Account's date of last edit

    Methods
    -------
    from_faker
        Generates fake Account.
        Powered by mighty Faker.

    """

    def __init__(
        self,
        item: str,
        url: str,
        username: str,
        password: str,
        notes: str,
        date_created: str,
        date_modified: str,
    ):
        """
        Parameters
        ----------
        item : str
            The item name (description) of an Account
        url : str
            The Account's website URL
        username: str
            The Account's username
        password: str
            The Account's password
        notes: str
            The Account's brief text notes
        date_created: str
            The Account's date of creation
            in '2020-01-26 13:52:01' format
        date_modified: str
            The Account's date of last edit
            in '2020-01-26 13:52:01' format

        """

        self.item = item
        self.url = url
        self.username = username
        self.password = password
        self.notes = notes
        self.date_created = date_created
        self.date_modified = date_modified

    @classmethod
    def from_faker(cls) -> Account:
        """
        Generates fake Account.
        Powered by mighty Faker.

        Returns
        -------
        Account
            Some randomly generated fake account

        """

        faker = Faker()
        item = faker.company()
        url = faker.url()
        username = faker.safe_email()
        password = PasswordGenerator("random", 8).generate_password()
        notes = "Some fake account created with Faker"
        date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_modified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return cls(item, url, username, password, notes, date_created, date_modified)

    def __repr__(self) -> str:
        return f"Account(item={self.item}, url={self.url}, username={self.username}, password={self.password}, notes={self.notes}, date_created={self.date_created}, date_modified={self.date_modified})"
