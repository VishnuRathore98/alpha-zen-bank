import random
import string
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_ph = PasswordHasher()


def generate_otp(length: int = 6) -> str:
    otp = "".join(random.choices(string.digits, k=length))
    return otp


def generate_password_hash(password: str) -> str:
    return _ph.hash(password)
