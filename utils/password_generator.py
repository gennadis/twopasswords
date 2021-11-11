import os
import string
from random import SystemRandom
from random import choice

from dotenv import load_dotenv

"""
------------------
IT"S ALL GOOD HERE
------------------
"""


load_dotenv()
WORDS: str = os.environ.get("WORDS")


class PasswordGenerator:
    """
    Password generation class.
    - generate random style password
    - generate XKCD style password
    - generate PIN style password
    """

    def __init__(self, style: str = "random", length: int = 16):
        self.style = style
        self.length = length
        self.alphabet = string.ascii_letters + string.digits + string.punctuation
        self.words_list = WORDS
        self.styles = ("random", "xkcd", "pin")

    def random_style(self) -> str:
        """
        Generete totally random password that contains
        letters, digits and punctuation symbols.
        At least 1 lowercase letter, 1 uppercase letter, 1 digit and 1 punct guaranteed.
        """
        letter_lower: list = SystemRandom().sample(string.ascii_lowercase, k=1)
        letter_upper: list = SystemRandom().sample(string.ascii_uppercase, k=1)
        digit: list = SystemRandom().sample(string.digits, k=1)
        punct: list = SystemRandom().sample(string.punctuation, k=1)
        rest: list = SystemRandom().sample(self.alphabet, k=self.length - 4)

        all_symbols: list = letter_lower + letter_upper + digit + punct + rest
        SystemRandom().shuffle(all_symbols)

        return "".join(all_symbols)

    def pin_style(self) -> str:
        """
        Generate PIN style password.
        Digits only.
        """
        return "".join([choice(string.digits) for _ in range(self.length)])

    # get words from a file
    def get_words(self) -> list:
        with open(self.words_list, "r") as wordlist:
            words: list = wordlist.readlines()

        return words

    def xkcd_style(self) -> str:
        """
        Generate XKCD style password from random words.
        See https://xkcd.com/936/ for more information.
        """
        words: list = self.get_words()
        password: str = "-".join(
            [SystemRandom().choice(words).strip() for _ in range(self.length)]
        )

        return password

    def generate_password(self) -> str:
        """
        Check password style and return accordingly.
        """
        if self.style == "random":
            return self.random_style()
        if self.style == "xkcd":
            return self.xkcd_style()
        if self.style == "pin":
            return self.pin_style()
        # else raise ValueError for style matching
        raise ValueError("Available styles: random, xkcd, pin")

    def __repr__(self) -> str:
        return f"PasswordGenerator{self.style, self.length}"


if __name__ == "__main__":
    random_pass = PasswordGenerator("random", 4).generate_password()
    print(random_pass)
    xkcd_pass = PasswordGenerator("xkcd", 4).generate_password()
    print(xkcd_pass)
    pin_pass = PasswordGenerator("pin", 6).generate_password()
    print(pin_pass)
    fast_pass = PasswordGenerator().generate_password()
    print(fast_pass)
