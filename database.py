from __future__ import annotations
import os
import dotenv
from datetime import datetime
from sqlcipher3 import dbapi2 as sqlite3
from faker import Faker
from password_generator import PasswordGenerator

"""
------------------
IT"S ALL GOOD HERE
------------------
"""


dotenv.load_dotenv()
DB_PATH = os.environ.get("DB_PATH")


def create_db(path: str, password: str, to_create=False) -> None:
    """
    Create a database:
        table acoounts:
            columns:
            1. id INTEGER PRIMARY KEY
            2. item TEXT
            3. url TEXT
            4. username TEXT
            5. password TEXT
            6. notes TEXT
            7. date_created TEXT
            8. date_modified TEXT
    """
    if to_create:
        connection = sqlite3.connect(path)
        if password is not None:
            connection.execute(f"pragma key = {password}")
        cursor = connection.cursor()
        cursor.execute(
            # """CREATE TABLE IF NOT EXISTS accounts (
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
    def __init__(self, path: str, password: str = None):
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()
        if password is not None:
            self.cursor.execute(f"pragma key={password}")

    def safe_push(self):
        self.connection.commit()
        # self.connection.close()

    def add_account(self, account: Account) -> None:
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

    def get_account(self, _item: str) -> Account:
        # self.cursor.execute("SELECT * FROM accounts WHERE url=:url;", {"url": _url})
        # self.cursor.execute("SELECT * FROM accounts WHERE item LIKE ?", _item)
        self.cursor.execute(
            "SELECT * FROM accounts WHERE item like '%{0}%'".format(_item)
        )

        return Account(*self.cursor.fetchone()[1:])  # [1:] -> without ID

    def get_exact_account(self, _item: str) -> Account:
        # self.cursor.execute("SELECT * FROM accounts WHERE url=:url;", {"url": _url})
        # self.cursor.execute("SELECT * FROM accounts WHERE item LIKE ?", _item)
        self.cursor.execute("SELECT * FROM accounts WHERE item=:item;", {"item": _item})

        return Account(*self.cursor.fetchone()[1:])  # [1:] -> without ID

    def get_all_accounts(self) -> list:
        self.cursor.execute("SELECT * FROM accounts")
        return [Account(*account[1:]) for account in self.cursor.fetchall()]

    def update_account(self, account: Account, password: str) -> None:
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
        self.cursor.execute(
            "DELETE FROM accounts WHERE url=:url AND username=:username",
            {"url": account.url, "username": account.username},
        )

    def clear_database(self) -> None:
        self.cursor.execute("DELETE FROM accounts")


class Account:
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
        self.item = item
        self.url = url
        self.username = username
        self.password = password
        self.notes = notes
        self.date_created = date_created
        self.date_modified = date_modified

    @classmethod
    def from_faker(cls):
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


if __name__ == "__main__":
    pass

    # create_db(DB_PATH, DB_PASSWORD, to_create=True)

    # db_session = DatabaseEngine(DB_PATH, DB_PASSWORD)
    # # print(db_session.get_all_accounts())
    # # print(db_session.get_account("http://www.wells.org/"))

    # for i in range(35):
    #     new_account = Account.from_faker()
    #     db_session.add_account(new_account)
    #     print(f"{new_account} added to database")

    # # for el in db_session.get_all_accounts():
    # #     print(*el, sep="  --  ")

    # # print(db_session.get_account("and"))

    # db_session.safe_push()

    # # new_account = Account("ping.com", "username11", "password111")
    # # new_account_2 = Account("sing.com", "username22", "password222")

    # # session.add_account(new_account)
    # # session.add_account(new_account_2)

    # # res = session.get_all_accounts()
    # # for el in res:
    # #     print(Account(*el[1:]))

    # # session.safe_push()
