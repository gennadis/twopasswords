import string
from random import SystemRandom, choice


class PasswordGenerator:
    """
    This class is responsible for all the Password generation
    operations needed in the code such as:
    - generating random style password
    - generating XKCD style password
    - generating PIN style password
    """

    def __init__(self, style: str = "random", length: int = 16):
        self.style = style
        self.length = length

    styles = ("random", "xkcd", "pin")

    # alphabet for random password generation
    alphabet: list = string.ascii_letters + string.digits + string.punctuation
    # txt file path for xkcd password generation
    words_path: str = "cryptog/words.txt"

    def random_style(self) -> str:
        """
        Generate totally random password.
        At least 1 of (lower, upper, number, punctuation) symbols shall be included.
        So length should be >= 4.
        """

        # TODO: more elegant implementation needed
        # - without HARDCODING LENGTH value
        # - without WHILE_TRUE

        if self.length < 4:
            self.length = 4

        while True:
            password = ""
            for _ in range(self.length):
                symbol = SystemRandom().choice(PasswordGenerator.alphabet)
                password += symbol

            if (
                # check if at least 1 lowercase letter in password
                any(char.islower() for char in password)
                # check if at least 1 uppercase letter in password
                and any(char.isupper() for char in password)
                # check if at least 1 digit symbol in password
                and any(char.isdigit() for char in password)
                # check if at least 1 punctuation symbol in password
                and any(char in string.punctuation for char in password)
            ):
                break

        return password

    def pin_style(self) -> str:
        """
        Generate PIN style password.
        Digits only.
        """
        self.alphabet = string.digits
        pin = "".join([choice(self.alphabet) for _ in range(self.length)])

        return pin

    # get words from a file
    @staticmethod
    def get_words() -> list:
        with open(PasswordGenerator.words_path, "r") as wordlist:
            words = wordlist.readlines()

        return words

    def xkcd_style(self) -> str:
        """Generate XKCD style password from random words.
        See https://xkcd.com/936/ for more information.
        """
        words = self.get_words()  # get words from a file
        password = "-".join(
            [SystemRandom().choice(words).strip() for _ in range(self.length)]
        )

        return password

    def generate_password(self) -> str:
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

    # def validate_password() -> str:
    #     """Validate generated XKCD-style password by user.
    #     Function implemented only for convenience of remembering the password.
    #     """
    #     accepted = False
    #     while not accepted:
    #         password = generate_xkcd()
    #         print(f"Generated password: {password}")
    #         accepted = input("Accept? [YES / NO] ").lower() in ["yes", "y"]
    #         # print(f'Password accepted: {str(accepted).upper()}')
    #     return password


if __name__ == "__main__":
    # PasswordGenerator class practice below...

    print(PasswordGenerator())  # repr test

    random_pass = PasswordGenerator("random", 8).generate_password()
    print(random_pass)
    xkcd_pass = PasswordGenerator("xkcd", 4).generate_password()
    print(xkcd_pass)
    pin_pass = PasswordGenerator("pin", 6).generate_password()
    print(pin_pass)

    # now let's check this with attributes set to default...
    fast_pass = PasswordGenerator().generate_password()
    print(fast_pass)

    # error_pass = PasswordGenerator("other_style", 9).generate_password()
    # print(error_pass)
