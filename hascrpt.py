#!/usr/bin/python


import hashlib


def hash_info(method, **kwargs):
    if method == "md5":
        return md5_hash(**kwargs)


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
