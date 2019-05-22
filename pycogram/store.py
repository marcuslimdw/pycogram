
from __future__ import annotations

# noinspection PyUnresolvedReferences
import crypt
import json
from secrets import compare_digest
from typing import Dict, Iterable, List

from .util import make_checksum, reverse

HASH_METHOD = crypt.METHOD_SHA256

KeyPassPair = Dict[str, str]

class PycoStore:

    def __init__(self, data: Dict[str, Group], checksum: str, salt: str):
        """
        Initialises a new PycoStore.

        Args:
            data: A group name-Group object mapping.
            checksum: The calculated checksum of the data.
            salt: The salt used to calculate the checksum.
        """
        self._data = data
        self.checksum = checksum
        self.salt = salt

    def __iter__(self) -> Iterable[Group]:
        return iter(self._data.values())

    def __getitem__(self, group_name: str) -> Group:
        try:
            return self._data[group_name]

        except KeyError:
            raise KeyError(f'The group {group_name} does not exist in the current Pycogram.')

    def __contains__(self, value: str) -> bool:
        return value in self._data

    def add_group(self, group_name: str, key: str, value: str) -> PycoStore:
        """
        Creates a new `PycoStore` with the named group inserted, containing a single key-value pair.

        Args:
            group_name: The name of the new `Group` to insert.
            key: The key that the new `Group` will contain.
            value: The value corresponding to `key`.

        Returns:
            A new `PycoStore` containing a `Group` named `group_name`.
        """
        self._should_not_contain(group_name)
        return self._insert(Group.new(group_name, key, value, self.checksum))

    def replace_key(self, group_name: str, key: str, value: str) -> PycoStore:
        """
        Creates a new `PycoStore` with a key-value pair in the named group replaced.

        Args:
            group_name: The name of the group to replace a pair from.
            key: The key to replace the value of.
            value: The new value.

        Returns:
            A new `PycoStore` with the value corresponding to `key` in `group_name` replaced with `value`..
        """
        self[group_name]._should_contain(group_name)
        return self._insert(self[group_name].lock(key, value, self.checksum))

    def save(self, path: str):
        with open(path, 'w') as f:
            json.dump({'checksum': self.checksum,
                       'salt': self.salt,
                       'data': {k: v.as_dict() for k, v in self._data.items()}}, f)

    @classmethod
    def from_dict(cls, data_dict: Dict[str, KeyPassPair], checksum: str, salt: str):
        """
        Creates a new `PycoStore` from a nested `dict`. Converts values to `Group` objects, then delegates to `__init__`.

        Args:
            data_dict: The `dict` containing group data.
            checksum: The calculated checksum of the data.
            salt: The salt used to calculate the checksum.

        Returns:
            A new `PycoStore`.
        """
        data = {group_name: Group(group_name, group_data) for group_name, group_data in data_dict.items()}
        return cls(data, checksum, salt)

    @classmethod
    def load(cls, path: str, master_key: str) -> PycoStore:
        """
        Loads a new `PycoStore` from a given path.

        Args:
            path: The path to the JSON file describing the object.
            master_key: The master key with which to perform encryption and decryption.

        Returns:
            The loaded `PycoStore`.
        """
        with open(path) as f:
            try:
                raw_data = json.load(f)
                checksum = raw_data['checksum']
                salt = raw_data['salt']
                data = raw_data['data']

            except (json.decoder.JSONDecodeError, KeyError):
                raise ValueError(f'{path} could not be parsed as a valid Pycogram file.')

        if compare_digest(make_checksum(master_key, salt), checksum):
            return cls.from_dict(data, checksum, salt)

        else:
            raise ValueError('The provided master key is incorrect.')

    def _insert(self, new_group: Group) -> PycoStore:
        """
        Creates a new PycoStore with the specified group inserted. Overrides any existing group with the same name.

        Args:
            new_group: The `Group` object to insert.

        Returns:
            A new `PycoStore` with `new_group` inserted.
        """
        new_data = {**self._data, new_group.name: new_group}
        return PycoStore(new_data, self.checksum, self.salt)

    def _should_not_contain(self, group_name: str):
        """
        Raises a ValueError if a group name is already used in this `PycoStore`.

        Args:
            group_name: The name of the group to check.

        Raises:
            ValueError if `group_name` already exists in this `PycoStore`

        """
        if group_name in self:
            raise ValueError(f'The group {group_name} already exists in the current Pycogram.')


class Group:

    def __init__(self, name: str, keystore: KeyPassPair):
        self.name = name
        self._keystore = keystore

    def __contains__(self, key):
        return key in self._keystore

    def __getitem__(self, key: str) -> str:
        return self._keystore[key]

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __eq__(self, other: Group):
        try:
            return (self.name == other.name) and (self._keystore == other._keystore)

        except (AttributeError, TypeError):
            return NotImplemented

    def keys(self) -> List[str]:
        return list(self._keystore.keys())

    def unlock(self, key: str, checksum: str) -> str:
        return reverse(self._keystore[key], checksum)

    def lock(self, key: str, value: str, checksum: str) -> Group:
        return Group(self.name, {**self._keystore, key: reverse(value, checksum)})

    def as_dict(self) -> KeyPassPair:
        return self._keystore

    @classmethod
    def new(cls, name: str, key: str, value: str, checksum: str) -> Group:
        return cls(name, {key: reverse(value, checksum)})

    def _should_contain(self, key: str):
        """
        Raises a ValueError if a key is not present in this `Group`.

        Args:
            key: The key to test for membership.

        Raises:
            ValueError if `key` does not exist in this `Group`.

        """
        if key not in self:
            raise ValueError(f'The key {key} does not exist in the group {self.name}.')

