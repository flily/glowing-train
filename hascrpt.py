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
        return hash_md5hex_hash("md5", **kwargs)

    elif method == "sha1-md5hex":
        return hash_md5hex_hash("sha1", **kwargs)

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


def get_password_object(method, value, **kwargs):
    o = {
        "type": method,
        "value": value,
    }

    if kwargs:
        o.update(kwargs)

    return o


def onetime_hash_hex(method, password, **kwargs):
    m = hashlib.new(method)
    m.update(password)
    h = m.hexdigest()

    o = {
        "password": get_password_object(method, h),
    }
    o.update(kwargs)
    return o


def hash_md5hex_hash(method, password, **kwargs):
    m = hashlib.new(method)
    m.update(password.lower())
    h = m.hexdigest()

    o = {
        "password": get_password_object("%s-md5hex" % method, h)
    }
    o.update(kwargs)
    return o


def onetime_salt_hash_hex(method, password, salt_length=16, **kwargs):
    salt = os.urandom(salt_length)
    m = hashlib.new(method)
    m.update(password)
    m.update(salt)
    h = m.hexdigest()

    o = {
        "password": get_password_object(method, h,
                                        salt=base64.b64encode(salt)),
    }
    o.update(kwargs)
    return o


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
        "password": get_password_object("multi-%s" % method, c,
                                        time=time)
    }


if __name__ == "__main__":
    name_list = ["method", "password", "salt_length"]
    test_cases = [
        ("md5", "foobar"),
        ("sha1", "foobar"),
        ("sha224", "foobar"),
        ("sha256", "foobar"),
        ("sha384", "foobar"),
        ("sha512", "foobar"),
        ("md5-md5hex", "3858f62230ac3c915f300c664312c63f"),
        ("salt-md5", "foobar"),
        ("salt-md5", "foobar", 32),
        ("salt-sha1", "foobar"),
        ("salt-sha1", "foobar", 32),
    ]

    for x in test_cases:
        input = dict(zip(name_list, x))
        input["email"] = "demo@example.com"
        input["phone"] = "13800000000"

        tab = hash_info(**input)
        print tab
        got = tab["password"]["value"]
        salt = tab["password"].get("salt", "")
        print "[%s] '%s' -> %s (%s)" % (input["method"], input["password"], got, salt)
