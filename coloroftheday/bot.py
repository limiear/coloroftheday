#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from twython import Twython, TwythonError
import model.database as db
from model import ColorHistory
from grapher import draw
from colordescriptor import rank_diff, describe
import time
from twitter_keys import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
import random
from StringIO import StringIO
import itertools
import chroma
import shelve


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
            'Hoy es recomendable un color %s.',
            'Algo %s es lo recomendado para hoy.',
            'Intenta utilizar algo %s.',
            'Prueba utilizar algo %s.',
            'Disfruta de algo %s.',
            'Utiliza algo %s.',
            'Aprecia algo %s.',
            'Relajate con algo %s.',
            'Inspirate con algo %s.',
        ]

    def upload_media(self, image):
        with open(image, 'rb') as photo:
            result = StringIO(photo.read())
        return result

    def tweet(self, status, images):
        time.sleep(10)
        medias = map(lambda i: self.upload_media(i), images)
        params = {'status': status}
        if medias:
            params['media'] = medias[0]
        # self.twitter.post('/statuses/update_with_media',
        #                  params=params)
        print status, len(status)

    @twython
    def coloroftheday_showcase(self, cache):
        history = ColorHistory(cache)
        self.color = history.get([datetime.today().date()])[0][1]
        c = chroma.Color('#%s' % self.color)
        name = describe(self.color)
        filename = draw(history, 'coloroftheday.png')
        codes_tp = "#%s; rgb:%i,%i,%i; cmyk:%i%%,%i%%,%i%%,%i%%"
        args = [[self.color], list(c.rgb256), map(lambda i: round(100 * i, 0),
                                             list(c.cmyk))]
        codes = codes_tp % tuple(itertools.chain.from_iterable(args))
        template = random.choice(self.intros)
        self.tweet(template % ('%s (%s)' % (name, codes)), filename)

    def lotery_showcase(self, cache):
        bets = shelve.open('betsoftheday')
        all_bets = map(lambda t: (t[1][0][1:], t[0]), bets.items())
        colors = {}
        for b in all_bets:
            colors.setdefault(b[0], []).append(b[1])
        users = lambda l: map(lambda u: '@%s' % u, l)
        if self.color in colors.keys():
            winners = colors[self.color]
            self.tweet('De %i participante/s hubo %i ganador/es: %s.' %
                        (len(all_bets), len(winners), ','.join(users(winners))), [])
        else:
            keys = colors.keys()
            rank = map(lambda c: rank_diff(c, self.color), keys)
            if rank:
                closest_color = keys[rank.index(min(rank))]
                self.tweet(('No hubo ganadores. '
                            'Cerca, con el #%s, estuvo/estuvieron: %s.') %
                           (closest_color,
                            ','.join(users(colors[closest_color]))), [])
            else:
                self.tweet('No hubo participantes. Para participar '
                           'envíame el código hexadecimal del color '
                           'por mensaje privado.')
        # os.remove(glob.glob('betsoftheday*')[0])

    def demonstrate(self):
        cache = db.open()
        self.coloroftheday_showcase(cache)
        if datetime.now().hour < 8:
            self.lotery_showcase(cache)
        db.close(cache)


presenter = Presenter()
presenter.demonstrate()
