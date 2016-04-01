#!/usr/bin/python


def check_email(email):
    if "@" not in email:
        return None

    return email.strip()
