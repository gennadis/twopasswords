from __future__ import annotations
import os
import dotenv
from typing import List, NewType
from sqlcipher3 import dbapi2 as sqlite3
from datetime import datetime


"""
------------------
IT"S ALL GOOD HERE
------------------
"""


dotenv.load_dotenv()
DB_PATH = os.environ.get("DB_PATH")
DB_PASSWORD = os.environ.get("DB_PASSWORD")


def create_db(path: str, password: str) -> None:
    """
    Create a database:
        table acoounts:
            columns:
            1. id INTEGER PRIMARY KEY
            2. url TEXT
            3. username TEXT
            4. password TEXT
    """
    connection = sqlite3.connect(path)
    if password is not None:
        connection.execute(f"pragma key = {password}")
    cursor = connection.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY,
        url TEXT,
        username TEXT,
        password TEXT
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

    def safe_quit(self):
        self.connection.commit()
        self.connection.close()

    def add_account(self, account: Account) -> None:
        self.cursor.execute(
            "INSERT INTO accounts (url, username, password) VALUES (:url, :username, :password)",
            {
                "url": account.url,
                "username": account.username,
                "password": account.password,
            },
        )

    def get_all_accounts(self) -> List:
        self.cursor.execute("SELECT * FROM accounts")
        return self.cursor.fetchall()

    def update_account(self, account: Account, password: str) -> None:
        self.cursor.execute(
            "UPDATE accounts SET password=:password WHERE url=:url AND username=:username",
            {
                "url": account.url,
                "username": account.username,
                "password": password,
            },
        )

    def delete_account(self, account: Account) -> None:
        self.cursor.execute(
            "DELETE FROM accounts WHERE url=:url AND username=:username",
            {"url": account.url, "username": account.username},
        )


class Account:
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password

    def __repr__(self) -> str:
        return f"Account(url={self.url}, username={self.username}, password={self.password})"


if __name__ == "__main__":

    new_password = "password1"
    create_db(DB_PATH, new_password)

    session = DatabaseEngine(DB_PATH, DB_PASSWORD)

    print(session.get_all_accounts())

    new_account = Account("ping.com", "username11", "password111")
    new_account_2 = Account("sing.com", "username22", "password222")

    session.add_account(new_account)
    session.add_account(new_account_2)

    res = session.get_all_accounts()
    for el in res:
        print(Account(*el[1:]))
