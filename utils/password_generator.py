"""
# TODO: should place some nice text here...

This module is responsible for password 
generation. Several password styles implemented:
totally random, XKCD style, PIN.

...

"""

import string
from random import SystemRandom, choice

from config import config_loader

# load configuration
file_paths, email_settings = config_loader.load()


class PasswordGenerator:

    """
    A class used to generate random passwords.
    Generates random, XKCD and pin passwords.

    https://xkcd.com/936/


    Attributes
    ----------
    style : str
        Password style:
        (Default is random for convenience)
            - totally random
            - XKCD style
            - PIN
    length : int
        Desired password length (default is 16)
    alphabet : str
        Desired symbols from which
        password will be generated
    words_list : str
        Path to a TXT file
        with words from which
        password will be generated
    styles : tuple
        Tuple with available styles


    Methods
    -------
    random_style
        Generates totally random password
        that consists of random symbols
        such as digits, letters, special chars.
        Uses SystemRandom and shuffle methods.
    pin_style
        Generates PIN style passwords.
        Contains digits only.
    get_words
        Loads words TXT file
        and creates list of words.
    xkcd_style
        Generates XKCD style password.
        See https://xkcd.com/936/
        for more information.
    generate_password
        Checks chosen password style
        and generates password accordingly.

    """

    def __init__(self, style: str = "random", length: int = 16):
        """
        Parameters
        ----------
        style : str
            Password style:
            (Default is random for convenience)
                - totally random
                - XKCD style
                - PIN
        length : int
            Desired password length
            (Default is 16, minimum is 4)
        alphabet : str
            Desired symbols from which
            password will be generated
        words_list : str
            Path to a TXT file
            with words from which
            password will be generated
        styles : tuple
            Tuple of strings with available styles

        """

        self.style = style
        self.length = length
        self.alphabet = string.ascii_letters + string.digits + string.punctuation
        self.words_list = file_paths["words"]
        self.styles = ("random", "xkcd", "pin")

    def random_style(self) -> str:
        """
        Generetes totally random password that
        contains letters, digits and punctuation
        symbols. At least 1 lowercase letter,
        1 uppercase letter, 1 digit and 1 punctuation
        symbols are guaranteed.

        Returns
        -------
        str
            Returns random password in string

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
        Generetes PIN style password.
        Contains digits only.

        Returns
        -------
        str
            Returns random PIN password

        """
        return "".join([choice(string.digits) for _ in range(self.length)])

    def get_words(self) -> list:
        """
        Loads words TXT file and returns
        list of words that will be used
        for XKCD style password generation.

        Returns
        -------
        list
            Returns list of words.
            By default returns list of 10_000
            English words from a words.txt file.

        """

        with open(self.words_list, "r") as wordlist:
            words: list = wordlist.readlines()

        return words

    def xkcd_style(self) -> str:
        """
        Generates XKCD style password.
        See https://xkcd.com/936/ for more information.

        Returns
        -------
        str
            Returns password that contains randomly
            chosen words separated by '-' symbol.

        """

        words: list = self.get_words()
        password: str = "-".join(
            [SystemRandom().choice(words).strip() for _ in range(self.length)]
        )

        return password

    def generate_password(self) -> str:
        """
        Checks chosen password style
        and generates password accordingly.

        Returns
        -------
        str
            Password generated accordingly
            to a chosen password style.

        Raises
        ------
        ValueError
            Raises error if chosen style not
            presented in self.styles parameter tuple.

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
