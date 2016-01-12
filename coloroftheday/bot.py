#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from populartwitterbot import Bot
from datetime import datetime
import model.database as db
from model import ColorHistory
from grapher import draw
from colordescriptor import rank_diff, describe
import time
import random
from StringIO import StringIO
import itertools
import chroma
import shelve
import requests
from PIL import Image


class Presenter(object):

    def __init__(self):
        self.load_config()
        self.twitter = Bot(self.config.items()[0])
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
        self.ratios = {}

    def load_config(self):
        if 'CONFIG' in os.environ:
            CONFIG = os.environ['CONFIG']
        else:
            with open('config.json') as f:
                CONFIG = f.read()
        self.config = json.loads(CONFIG)
        self.screen_name = self.config['coloroftheday']['screen_name']

    def upload_media(self, image):
        with open(image, 'rb') as photo:
            result = StringIO(photo.read())
        return result

    def tweet(self, status, images):
        time.sleep(10)
        medias = map(lambda i: self.upload_media(i), images)
        params = {'status': status}
        if not images:
            self.twitter.update_status(status=status)
        else:
            params['media'] = medias[0]
            self.twitter._post('/statuses/update_with_media',
                               params=params)
        print status, len(status)

    def coloroftheday_showcase(self, cache):
        history = ColorHistory(cache)
        self.color = history.get([datetime.today().date()])[0][1]
        c = chroma.Color('#%s' % self.color)
        self.color_rgb = c.rgb256
        name = describe(self.color)
        filename = draw(history, 'coloroftheday.png')
        codes_tp = "#%s; rgb:%i,%i,%i; cmyk:%i%%,%i%%,%i%%,%i%%"
        args = [[self.color], list(self.color_rgb),
                map(lambda i: round(100 * i, 0),
                    list(c.cmyk))]
        codes = codes_tp % tuple(itertools.chain.from_iterable(args))
        template = random.choice(self.intros)
        self.tweet(template % ('%s (%s)' % (name, codes)), filename)

    def scrap_followers(self, method=None):
        self.followers = []
        ready = False
        cursor = -1
        while not ready:
            response = self.twitter._get("/followers/list",
                                         {"screen_name": self.screen_name,
                                          "cursor": cursor,
                                          "count": 200})
            self.followers.extend(response['users'])
            if method:
                map(method, response['users'])
            cursor = response['next_cursor']
            ready = cursor == 0

    def download_profile_image(self, profile, path='.'):
        url = profile['profile_image_url']
        response = requests.get(url, stream=True)
        filename = None
        if response.status_code == 200:
            filename = '{:}/{:}.{:}'.format(path,
                                            profile['screen_name'],
                                            url.split('.')[-1])
            with open(filename, 'wb') as handle:
                for block in response.iter_content(1024):
                    handle.write(block)
        return filename

    def rank_image(self, filename):
        im = Image.open(filename)
        data = list(im.getdata())
        data = map(tuple, data)
        diff = lambda b: abs(b[0] - b[1]) <= 20
        data = map(lambda c: tuple(map(lambda b: b[0] if diff(b) else 255,
                                       zip(c, self.color_rgb))),
                   data)
        total = im.size[0] * im.size[1] * 3  # 3 bands (RGB)
        win = sum(map(lambda c: sum(map(diff, zip(c, self.color_rgb))), data))
        ratio = float(win) / float(total)
        im.putdata(data)
        path = 'ranked'
        if not os.path.exists(path):
            os.makedirs(path)
        output = '{:}/{:}'.format(path, filename.split('/')[-1])
        im.save(output)
        im.close()
        self.ratios.setdefault(ratio, []).append(output)

    def analyze_profile(self, profile):
        path = 'followers'
        if not os.path.exists(path):
            os.makedirs(path)
        if not profile["default_profile_image"]:
            filename = self.download_profile_image(profile, path)
            try:
                self.rank_image(filename)
            except Exception:
                print profile['screen_name']

    def we_saw_you_showcase(self, cache):
        os.system("rm -rf followers ranked")
        self.scrap_followers(self.analyze_profile)
        rank = sorted(self.ratios.keys(), reverse=True)
        rank.remove(0)
        rank = rank[:min(3, len(rank))]
        self.tweet("Podio de los seguidores que poseen el"
                   " color del día en su imágen de perfil...", [])
        medal = ["El oro", "La plata", "El bronce"]
        for r in reversed(rank):
            name = lambda f: (f.split('/')[-1]).split('.')[-2]
            names = " ".join(map(lambda f: '@' + name(f), self.ratios[r]))

            self.tweet("%s es para %s con (%.1f %%)" % (medal[rank.index(r)],
                                                        names,
                                                        r), self.ratios[r])

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
                       (len(all_bets), len(winners),
                        ','.join(users(winners))), [])
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
        if datetime.now().hour <= 8:
            self.lotery_showcase(cache)
            self.we_saw_you_showcase(cache)
        db.close(cache)


presenter = Presenter()
presenter.demonstrate()
