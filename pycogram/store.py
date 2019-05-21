
from __future__ import annotations

# noinspection PyUnresolvedReferences
import crypt
import json
from secrets import compare_digest
from typing import Dict, Iterable

from .util import make_checksum, reverse

HASH_METHOD = crypt.METHOD_SHA256


class PycoStore:

    def __init__(self, data: Dict[str, Group], checksum: str, salt: str):
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

    def __contains__(self, value: str):
        return value in self._data

    def add(self, group_name: str, key: str, value: str):
        self._should_not_contain(group_name)
        return self._insert(group_name, Group.new(group_name, key, value, self.checksum))

    def replace(self, group_name: str, key: str, value: str):
        return self._insert(group_name, self[group_name].lock(key, value, self.checksum))

    def save(self, path: str):
        with open(path, 'w') as f:
            json.dump({'checksum': self.checksum,
                       'salt': self.salt,
                       'data': {k: v.as_dict() for k, v in self._data.items()}}, f)

    @classmethod
    def from_dict(cls, data_dict: Dict[str, Dict[str, str]], checksum: str, salt: str):
        data = {group_name: Group(group_name, group_data) for group_name, group_data in data_dict.items()}
        return cls(data, checksum, salt)

    @classmethod
    def load(cls, path: str, master_key: str) -> PycoStore:
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

    def _insert(self, group_name: str, new_group: Group):
        new_data = {**self._data, group_name: new_group}
        return PycoStore(new_data, self.checksum, self.salt)

    def _should_not_contain(self, group_name: str):
        if group_name in self:
            raise ValueError(f'The group {group_name} already exists in the current Pycogram.')


class Group:

    def __init__(self, name: str, keystore: Dict[str, str]):
        self._name = name
        self._keystore = keystore

    def __getitem__(self, key: str) -> str:
        return self._keystore[key]

    def __str__(self):
        return self._name

    def __repr__(self):
        return self._name

    def __eq__(self, other: Group):
        try:
            return (self._name == other._name) and (self._keystore == other._keystore)

        except (AttributeError, TypeError):
            return NotImplemented

    def keys(self):
        return list(self._keystore.keys())

    def unlock(self, key: str, checksum: str) -> str:
        return reverse(self._keystore[key], checksum)

    def lock(self, key: str, value: str, checksum: str) -> Group:
        return Group(self._name, {**self._keystore, key: reverse(value, checksum)})

    def as_dict(self):
        return self._keystore

    @classmethod
    def new(cls, name: str, key: str, value: str, checksum: str):
        return cls(name, {key: reverse(value, checksum)})
