import pytest

from pycogram.store import PycoStore, Group


@pytest.fixture
def master_key():
    return 'g.bRK6lO9JhFT/TP'


@pytest.fixture
def checksum():
    return '$5$Cu6AjoXCxAdwqfXB$/HpFN/pral5sDLNYQ.XsszEyx0I75SAoHc7p3S13p4B'


@pytest.fixture
def salt():
    return ''


@pytest.fixture
def group_a():
    return Group('test_group_a',
                 {'key': 'RTH6\x10'})


@pytest.fixture
def group_b():
    return Group('test_group_b',
                 {'key': 'RTH6\x10'})


@pytest.fixture
def group_raw():
    return Group('test_group_raw',
                 {})


@pytest.fixture()
def store(checksum, group_a, group_b, salt):
    return PycoStore({'test_group_a': group_a,
                      'test_group_b': group_b},
                     checksum,
                     salt)


class TestPycoStore:

    def test___getitem__(self, store, group_a, group_b):
        assert store['test_group_a'] == group_a
        assert store['test_group_b'] == group_b

    def test_replace(self, store, checksum):
        replaced = store.replace_key('test_group_a', 'key', 'new_pass')
        assert replaced['test_group_a'].unlock('key', checksum) == 'new_pass'


class TestGroup:

    def test_keys(self, group_a):
        assert group_a.keys() == ['key']

    def test_unlock(self, group_a, checksum):
        assert group_a.unlock('key', checksum) == 'value'

    def test_lock(self, group_raw, checksum):
        assert group_raw.lock('key', 'value', checksum)['key'] == 'RTH6\x10'

    def test___getitem__(self, group_a):
        assert group_a['key'] == 'RTH6\x10'
