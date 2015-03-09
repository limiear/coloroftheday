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

    def upload_media(self, image):
        photo = open(image, 'rb')
        return self.twitter.upload_media(media=photo)

    def tweet(self, status, images):
        time.sleep(10)
        template = "%s"
        #medias = map(lambda i: self.upload_media(i)['media_id'], images)
        #self.twitter.update_status(medias_id=medias,
        #                           status=template % status)
        print template % status

    @twython
    def coloroftheday_showcase(self, cache):
        history = ColorHistory(cache)
        color = history.get([datetime.today().date()])[0][1]
        name = describe(color)
        filename = draw(history, 'coloroftheday.png')
        self.tweet(name, filename)

    def demonstrate(self):
        cache = db.open()
        self.coloroftheday_showcase(cache)
        db.close(cache)


presenter = Presenter()
presenter.demonstrate()