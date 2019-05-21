import pytest

from pycogram.util import make_salt, reverse, format_key_tree
from pycogram.store import Group


def test_make_salt():
    assert len(make_salt()) == 19


@pytest.mark.parametrize('value', ['short', 'a_really_long_key!', 'F7041k70CB90jUvp'])
def test_reverse(value):
    salt = make_salt()
    assert reverse(reverse(value, salt), salt) == value


@pytest.mark.xfail
def test_format_key_tree():
    result = format_key_tree('test_store',
                             [Group('test_group_a', {'key_1': 'value_1',
                                                     'key_2': 'value_2'}),
                              Group('test_group_b', {'key_1': 'value_1'})])

    expected = '''test_store
                    |-- test_group_a
                    |    |-- key_1
                    |    |-- key_2
                    |-- test_group_b
                         |-- key_1'''

    assert result == expected
