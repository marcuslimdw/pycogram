from __future__ import annotations

# noinspection PyUnresolvedReferences
import crypt
from itertools import cycle
from typing import Iterable

HASH_METHOD = crypt.METHOD_SHA256


def make_checksum(master_key: str, salt: str) -> str:
    return crypt.crypt(master_key, salt)


def make_salt() -> str:
    return crypt.mksalt(HASH_METHOD)


def reverse(value: str, key: str) -> str:
    return ''.join(chr(ord(left) ^ ord(right)) for left, right in zip(value, cycle(key)))


# noinspection PyUnusedLocal
def format_key_tree(path: str, groups: Iterable) -> str:
    return '\n'.join(f'Keys for {group}: {group.keys()}' for group in groups)
