#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from twython import Twython, TwythonError
import model.database as db
from model import ColorHistory
from grapher import draw
from colordescriptor import describe
import time
from twitter_keys import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
import random
from StringIO import StringIO
import itertools
import chroma


def twython(func):
    def func_wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except TwythonError as e:
            print e
    return func_wrapper


class Presenter(object):

    def __init__(self):
        self.twitter = Twython(
            APP_KEY,
            APP_SECRET,
            OAUTH_TOKEN,
            OAUTH_TOKEN_SECRET
        )
        self.intros = [
            'El color del dia es %s.',
            'Hoy es recomendable utilizar un color %s.',
            'Algo %s es lo recomendado para hoy.',
            'Intenta utilizar algo %s.',
            'Prueba utilizar algo %s.',
            'Disfruta de algo %s.',
            'Te propongo algo %s como color del día.',
            'Aprecia algo %s, dado que es el color del día.',
            'Disfruta de algo %s, dado que es el color del día.',
        ]

    def upload_media(self, image):
        with open(image, 'rb') as photo:
            result = StringIO(photo.read())
        return result

    def tweet(self, status, images):
        time.sleep(10)
        template = random.choice(self.intros)
        medias = map(lambda i: self.upload_media(i), images)
        self.twitter.post('/statuses/update_with_media',
                          params={'status': template % status,
                                  'media': medias[0]})
        print template % status, len(template % status)

    @twython
    def coloroftheday_showcase(self, cache):
        history = ColorHistory(cache)
        color = history.get([datetime.today().date()])[0][1]
        c = chroma.Color('#%s' % color)
        name = describe(color)
        filename = draw(history, 'coloroftheday.png')
        codes_tp = "#%s; rgb:%i,%i,%i; cmyk:%s,%s,%s,%s"
        args = [[color], list(c.rgb256), map(lambda i: str(round(i, 3)), list(c.cmyk))]
        codes = codes_tp % tuple(itertools.chain.from_iterable(args))
        self.tweet('%s (%s)' % (name, codes), filename)

    def demonstrate(self):
        cache = db.open()
        self.coloroftheday_showcase(cache)
        db.close(cache)


presenter = Presenter()
presenter.demonstrate()
