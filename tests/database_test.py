import unittest
import abstract
from coloroftheday.model import database as db
import os


class TestDatabase(abstract.TestCase):

    def setUp(self):
        self.remove('cache*')
        self.cache = db.open()

    def tearDown(self):
        db.close(self.cache)

    def test_get(self):
        self.assertFalse(db.has_path(self.cache, 'key1'))
        data = db.get(self.cache, 'key1')
        self.assertEquals(data, {})
        self.assertTrue(db.has_path(self.cache, 'key1'))

    def test_get_with_path(self):
        self.assertFalse(db.has_path(self.cache, 'key1/child1'))
        data = db.get(self.cache, 'key1/child1')
        self.assertEquals(data, {})
        self.assertTrue(db.has_path(self.cache, 'key1'))
        self.assertTrue(db.has_path(self.cache['key1'], 'child1'))

    def test_set(self):
        self.assertFalse(db.has_path(self.cache, 'key1'))
        db.set(self.cache, 'key1', 123)
        data = db.get(self.cache, 'key1')
        self.assertEquals(data, 123)
        self.assertTrue(db.has_path(self.cache, 'key1'))

    def test_set_with_path(self):
        self.assertFalse(db.has_path(self.cache, 'key1/child1'))
        db.set(self.cache, 'key1/child1', 123)
        data = db.get(self.cache, 'key1/child1')
        self.assertEquals(data, 123)
        self.assertTrue(db.has_path(self.cache, 'key1'))
        self.assertTrue(db.has_path(self.cache['key1'], 'child1'))
        self.assertEquals(self.cache['key1']['child1'], 123)


if __name__ == '__main__':
    unittest.main()
