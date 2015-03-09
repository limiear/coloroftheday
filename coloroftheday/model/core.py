import database as db
import datetime
import requests


class Variable(object):

    def __init__(self, cache):
        self.cache = cache
        self.name = 'global'
        self.description = ''
        self.reference = ''

    @property
    def today(self):
        return datetime.datetime.now().date()

    def request(self, url):
        return requests.get(url).text

    def scrap(self, date_list):
        pass

    def should_scrap(self, date):
        serie = db.get(self.cache, self.name)
        return (date not in serie.keys()
                or (serie[date] in [None, []]))

    def get_element(self, date):
        # Return a value
        if isinstance(date, datetime.datetime):
            date = date.date()
        if self.should_scrap(date):
            value = self.scrap([date])
            value = value[0] if len(value) else value
            var = db.get(self.cache, self.name)
            var[date] = value
            db.set(self.cache, self.name, var)
            db.sync(self.cache)
        data = db.get(self.cache, self.name)
        return data[date] if date in data.keys() else None

    def get(self, date_list=[]):
        # Return a list of tuples with date and value for each tuple
        return map(lambda d: (d, self.get_element(d)), date_list)
