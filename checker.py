#!/usr/bin/python


import re


def check_email(email):
    if "@" not in email:
        return None

    return email.strip()


_phone_regex = re.compile("^\+?[0-9- ]+$")


def check_phone(phone):
    p = str(phone)
    if _phone_regex.match(p) is None:
        return None

    return p.strip()


if __name__ == "__main__":
    _cases = [
        "138 0000 0000",
        "+86 13800000000",
        "138-0000-0000",
        "+86-138-0000-0000",
        "0086-138-0000-0000",
        "138-MY-APPLE",
        138000000000,
    ]
    for x in _cases:
        print x, check_phone(x)
