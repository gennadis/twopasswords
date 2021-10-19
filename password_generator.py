import os
import string
import dotenv
from random import SystemRandom, choice


"""
------------------
IT"S ALL GOOD HERE
------------------
"""


dotenv.load_dotenv()
WORDS = os.environ.get("WORDS")


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
        At least 1 letter, 1 digit and 1 punct guaranteed.
        """
        letters = SystemRandom().sample(population=string.ascii_letters, k=1)
        digits = SystemRandom().sample(population=string.digits, k=1)
        puncts = SystemRandom().sample(population=string.punctuation, k=1)
        other = SystemRandom().sample(population=self.alphabet, k=self.length - 3)
        all = letters + digits + puncts + other
        SystemRandom().shuffle(all)
        return "".join(all)

    def pin_style(self) -> str:
        """
        Generate PIN style password.
        Digits only.
        """
        return "".join([choice(string.digits) for _ in range(self.length)])

    # get words from a file
    def get_words(self) -> list:
        with open(self.words_list, "r") as wordlist:
            words = wordlist.readlines()

        return words

    def xkcd_style(self) -> str:
        """
        Generate XKCD style password from random words.
        See https://xkcd.com/936/ for more information.
        """
        words = self.get_words()
        password = "-".join(
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
    random_pass = PasswordGenerator("random", 8).generate_password()
    print(random_pass)
    xkcd_pass = PasswordGenerator("xkcd", 4).generate_password()
    print(xkcd_pass)
    pin_pass = PasswordGenerator("pin", 6).generate_password()
    print(pin_pass)
    fast_pass = PasswordGenerator().generate_password()
    print(fast_pass)
