#!/usr/bin/python


import os
import base64
import hashlib


def hash_info(method, **kwargs):
    """

    :param method:
    :type method: str
    :param kwargs:
    :return:
    """
    if method == "md5":
        return onetime_hash_hex("md5", **kwargs)

    elif method == "sha1":
        return onetime_hash_hex("sha1", **kwargs)

    elif method in ["sha224", "sha256", "sha384", "sha512"]:
        return onetime_hash_hex(method, **kwargs)

    elif method == "md5-md5hex":
        return md5_md5hex_hash(**kwargs)

    elif method == "plain":
        return raw_dump("plain", **kwargs)

    elif method.startswith("raw-"):
        return raw_dump(method[4:].lower(), **kwargs)

    elif method.startswith("salt-"):
        return onetime_salt_hash_hex(method[5:], **kwargs)

    elif method.startswith("multi-"):
        parts = method.split("-")
        hash_method = parts[1]
        hash_times = int(parts[2])
        return iterate_hash(hash_method, time=hash_times, **kwargs)


def raw_dump(method, email, password, **kwargs):
    return {
        "email": email,
        "password": {
            "type": method,
            "value": password.lower(),
        }
    }


def onetime_hash_hex(method, email, password, **kwargs):
    m = hashlib.new(method)
    m.update(password)
    h = m.hexdigest()

    return {
        "email": email,
        "password": {
            "type": method,
            "value": h,
        }
    }


def md5_md5hex_hash(email, password, **kwargs):
    m = hashlib.new("md5")
    m.update(password.lower())
    h = m.hexdigest()

    return {"email": email, "password": {"type": "md5-md5hex", "value": h}}


def onetime_salt_hash_hex(method, email, password, salt_length=16, **kwargs):
    salt = os.urandom(salt_length)
    m = hashlib.new(method)
    m.update(password)
    m.update(salt)
    h = m.hexdigest()

    return {
        "email": email,
        "password": {
            "type": method,
            "value": h,
            "salt": base64.b64encode(salt),
        }
    }


def iterate_hash(method, email, password, time, **kwargs):
    i = 0
    c = password

    while i < time:
        m = hashlib.new(method)
        m.update(c)
        c = m.hexdigest()
        i += 1

    return {
        "email": email,
        "password": {
            "type": "multi-%s" % method,
            "time": time,
            "value": c,
        }
    }

