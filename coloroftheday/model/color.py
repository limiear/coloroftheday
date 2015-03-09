from core import Variable
import random


class ColorHistory(Variable):

    def __init__(self, cache):
        super(ColorHistory, self).__init__(cache)
        self.name = 'colors/selected'
        self.description = 'Selected colors.'
        self.reference = ''

    def scrap(self, date_list):
        return ['%06x' % random.randrange(16**6)]
