import unittest
import abstract
from coloroftheday.model import database as db
from coloroftheday.model.core import Variable
import os
import datetime
import requests


class TestCore(abstract.TestCase):

    def setUp(self):
        self.remove('cache*')
        self.cache = db.open()
        self.var = Variable(self.cache)
        self.today = datetime.datetime.now().date()
        self.yesterday = self.today - datetime.timedelta(days=1)

    def tearDown(self):
        db.close(self.cache)

    def set_key_value(self, date, value):
        v = db.get(self.cache, self.var.name)
        v[date] = value
        db.set(self.cache, self.var.name, v)
        db.sync(self.cache)

    def test_today(self):
        self.assertEquals(self.var.today, self.today)

    def test_request(self):
        url = 'http://ecolell.github.io/2014/11/16/welcome.html'
        page = self.var.request(url)
        self.assertEquals(page, requests.get(url).text)
        url = 'http://ecolell.github.io/2014/12/02/thesis.html'
        page = self.var.request(url)
        self.assertEquals(page, requests.get(url).text)

    def test_scrap(self):
        self.assertEquals(self.var.scrap(self.today), None)

    def test_should_scrap(self):
        # The first time should scrap.
        should = self.var.should_scrap(self.today)
        self.assertTrue(should)
        should = self.var.should_scrap(self.yesterday)
        self.assertTrue(should)
        # But if it return something, it should stop the scrapping for that
        # day.
        self.set_key_value(self.yesterday, [1.0])
        should = self.var.should_scrap(self.yesterday)
        self.assertFalse(should)
        should = self.var.should_scrap(self.today)
        self.assertTrue(should)
        self.set_key_value(self.today, [1.0])
        should = self.var.should_scrap(self.today)
        self.assertFalse(should)

    def test_get_element(self):
        # It should return and save the scraped value.
        self.var.scrap = lambda date_list: [1.25]
        value = self.var.get_element(self.yesterday)
        self.assertEquals(value, 1.25)
        self.var.scrap = lambda date_list: [2.35]
        value = self.var.get_element(self.today)
        self.assertEquals(value, 2.35)
        # If a value was saved, it should priorize the saved copy.
        value = self.var.get_element(self.yesterday)
        self.assertEquals(value, 1.25)

    def test_get(self):
        # It load the cache with data.
        self.test_get_element()
        # It query by a date_list.
        values = self.var.get([self.today, self.yesterday])
        self.assertEquals(values,
                          [
                              (self.today, 2.35),
                              (self.yesterday, 1.25)
                          ])
        values = self.var.get([self.yesterday, self.today])
        self.assertEquals(values,
                          [
                              (self.yesterday, 1.25),
                              (self.today, 2.35)
                          ])


if __name__ == '__main__':
    unittest.main()
