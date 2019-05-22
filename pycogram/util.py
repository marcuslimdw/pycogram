from __future__ import annotations

# noinspection PyUnresolvedReferences
import crypt
from itertools import cycle
from typing import Iterable

HASH_METHOD = crypt.METHOD_SHA256


def make_checksum(master_key: str, salt: str) -> str:
    """
    Generates a checksum from a master key and a salt, used to determine if the master key is valid.

    Args:
        master_key: The master key to validate.
        salt: The salt with which to generate the checksum.

    Returns:
        The created checksum.
    """
    return crypt.crypt(master_key, salt)


def reverse(value: str, key: str) -> str:
    """
    Performs encryption or decryption of a value.

    Notes:
        As this operation is XOR-based, it is symmetric.

    Args:
        value: The value to encrypt/decrypt.
        key: The key with which to perform encryption/decryption.

    Returns:
        The encrypted/decrypted string.
    """
    return ''.join(chr(ord(left) ^ ord(right)) for left, right in zip(value, cycle(key)))


# TODO: This should actually be annotated Iterable[Group], but it causes a circular import. Definitely fixable.
# noinspection PyUnusedLocal
def format_key_tree(name: str, groups: Iterable) -> str:
    """
    Converts a set of groups to a human-readable tree format.

    Notes:
         Not completely implemented.

    Args:
        name: A `PycoStore` name, forming the head node.
        groups: The groups to format.

    Returns:
        A string representation of a `PycoStore`'s tree structure.
    """
    return '\n'.join(f'Keys for {group}: {group.keys()}' for group in groups)
