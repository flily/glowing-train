#!/usr/bin/python


import hashlib


def hash_info(method, **kwargs):
    """

    :param method:
    :type method: str
    :param kwargs:
    :return:
    """
    if method == "md5":
        return md5_hash(**kwargs)

    elif method == "sha1":
        return sha1_hash(**kwargs)

    elif method.startswith("raw"):
        return raw_dump(method[3:].lower(), **kwargs)


def raw_dump(method, email, password):
    return {
        "email": email,
        "password": {
            "type": method,
            "value": password.lower(),
        }
    }


def md5_hash(email, password):
    m = hashlib.new("md5")
    m.update(password)
    h = m.hexdigest()

    return {"email": email, "password": {"type": "md5", "value": h}}


def sha1_hash(email, password):
    m = hashlib.new("sha1")
    m.update(password)
    h = m.hexdigest()

    return {"email": email, "password": {"type": "sha1", "value": h}}