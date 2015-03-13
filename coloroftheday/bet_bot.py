#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from twython import Twython, TwythonError
import shelve
import time
from twitter_keys import APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET
import random
import chroma
import re


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
        self.rest = 0
        self.bets = shelve.open('betsoftheday')

    def update_limit(self):
        self.rest = int(self.twitter.
                        get_lastfunction_header('x-rate-limit-remaining'))

    def __del__(self):
        self.bets.close()

    def read_news(self):
        dms = self.twitter.get_direct_messages(count=180)
        self.update_limit()
        d = lambda s: datetime.strptime(s, "%a %b %d %H:%M:%S +0000 %Y")
        s = lambda m, attr: m['sender'][attr]
        bet = lambda m: m[m.index('#'):m.index('#')+6]
        scrap = lambda m: (str(s(m,'screen_name')),
                           [s(m, 'id'), s(m,'name'), m['text'],
                            d(m['created_at'])])
        has_bet = lambda dm: re.search('#[0-9a-f]{6}', dm[1][2])
        dms = filter(has_bet, map(scrap, dms))
        bet = lambda dm: (dm[0], [dm[1][0], dm[1][1], has_bet(dm).group(0),
                                  dm[1][3]])
        return map(bet, dms)

    def say(self, status, user):
        if self.rest <= 1:
            return False
        print status, len(status)
        self.twitter.send_direct_message(user_id=user, text=status)
        self.rest -= 1
        print '-'
        return True

    def update_bet(self, detail):
        user, (user_id, name, bet, new_datetime) = detail
        response = ('', None)
        if user in self.bets:
            old_bet, old_datetime = self.bets[user]
            if old_datetime < new_datetime:
                if self.bets[user] == bet:
                    response = ('%s, entonces te mantengo la misma apuesta (%s).' %
                                (name, bet), user_id)
                else:
                    response = ('%s, he reemplazado tu apuesta de %s a %s.' %
                                (name, old_bet, bet), user_id)
        else:
            response = ('%s ha sido registrado como tu apuesta.' % bet, user_id)
        if response[1]:
            if self.say(*response):
                self.bets[user] = [bet, new_datetime]

    @twython
    def takebets_showcase(self, bets):
        news = self.read_news()
        map(self.update_bet, news)

    def demonstrate(self):
        self.takebets_showcase(self.bets)


presenter = Presenter()
presenter.demonstrate()
