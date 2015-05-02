# -*- coding: utf-8 -*-

"""
Copyright 2014 Randal S. Olson

This file is part of the Twitter Follow Bot library.

The Twitter Follow Bot library is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or (at your option) any
later version.

The Twitter Follow Bot library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with the Twitter
Follow Bot library. If not, see http://www.gnu.org/licenses/.
"""

from coloroftheday.twitter_keys import *
from twitter import Twitter, OAuth, TwitterHTTPError
import os
import itertools
import random

# put your tokens, keys, secrets, and Twitter handle in the following variables
TWITTER_HANDLE = "elcolordeldia"

# put the full path and file name of the file you want to store your "already followed"
# list in
ALREADY_FOLLOWED_FILE = "already-followed.csv"

t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
            APP_KEY, APP_SECRET))


def search_tweets(q, count=100, result_type="recent"):
    """
        Returns a list of tweets matching a certain phrase (hashtag, word, etc.)
    """

    return t.search.tweets(q=q, result_type=result_type, count=count)


def auto_fav(q, count=100, result_type="recent"):
    """
        Favorites tweets that match a certain phrase (hashtag, word, etc.)
    """

    result = search_tweets(q, count, result_type)

    for tweet in result["statuses"]:
        try:
            # don't favorite your own tweets
            if tweet["user"]["screen_name"] == TWITTER_HANDLE:
                continue

            result = t.favorites.create(_id=tweet["id"])
            print("favorited: %s" % (result["text"].encode("utf-8")))

        # when you have already favorited a tweet, this error is thrown
        except TwitterHTTPError as e:
            print("error: %s" % (str(e)))


def auto_rt(q, count=100, result_type="recent"):
    """
        Retweets tweets that match a certain phrase (hashtag, word, etc.)
    """

    result = search_tweets(q, count, result_type)

    for tweet in result["statuses"]:
        try:
            # don't retweet your own tweets
            if tweet["user"]["screen_name"] == TWITTER_HANDLE:
                continue

            result = t.statuses.retweet(id=tweet["id"])
            print("retweeted: %s" % (result["text"].encode("utf-8")))

        # when you have already retweeted a tweet, this error is thrown
        except TwitterHTTPError as e:
            print("error: %s" % (str(e)))


def get_do_not_follow_list():
    """
        Returns list of users the bot has already followed.
    """

    # make sure the "already followed" file exists
    if not os.path.isfile(ALREADY_FOLLOWED_FILE):
        with open(ALREADY_FOLLOWED_FILE, "w") as out_file:
            out_file.write("")

        # read in the list of user IDs that the bot has already followed in the
        # past
    do_not_follow = set()
    dnf_list = []
    with open(ALREADY_FOLLOWED_FILE) as in_file:
        for line in in_file:
            dnf_list.append(int(line))

    do_not_follow.update(set(dnf_list))
    del dnf_list

    return do_not_follow


def auto_follow(q, count=100, result_type="recent"):
    """
        Follows anyone who tweets about a specific phrase (hashtag, word, etc.)
    """

    result = search_tweets(q, count, result_type)
    following = set(t.friends.ids(screen_name=TWITTER_HANDLE)["ids"])
    do_not_follow = get_do_not_follow_list()

    for tweet in result["statuses"]:
        try:
            if (tweet["user"]["screen_name"] != TWITTER_HANDLE and
                    tweet["user"]["id"] not in following and
                    tweet["user"]["id"] not in do_not_follow):

                t.friendships.create(user_id=tweet["user"]["id"], follow=False)
                following.update(set([tweet["user"]["id"]]))

                print("followed %s" % (tweet["user"]["screen_name"]))

        except TwitterHTTPError as e:
            print("error: %s" % (str(e)))

            # quit on error unless it's because someone blocked me
            if "blocked" not in str(e).lower():
                quit()


def auto_follow_followers_for_user(user_screen_name, count=100):
    """
        Follows the followers of a user
    """
    following = set(t.friends.ids(screen_name=TWITTER_HANDLE)["ids"])
    followers_for_user = set(t.followers.ids(screen_name=user_screen_name)["ids"][:count]);
    do_not_follow = get_do_not_follow_list()

    for user_id in followers_for_user:
        try:
            if (user_id not in following and
                user_id not in do_not_follow):

                t.friendships.create(user_id=user_id, follow=False)
                print("followed %s" % user_id)

        except TwitterHTTPError as e:
            print("error: %s" % (str(e)))

def auto_follow_followers():
    """
        Follows back everyone who's followed you
    """

    following = set(t.friends.ids(screen_name=TWITTER_HANDLE)["ids"])
    followers = set(t.followers.ids(screen_name=TWITTER_HANDLE)["ids"])

    not_following_back = followers - following

    for user_id in not_following_back:
        try:
            t.friendships.create(user_id=user_id, follow=False)
        except Exception as e:
            print("error: %s" % (str(e)))


def auto_unfollow_nonfollowers():
    """
        Unfollows everyone who hasn't followed you back
    """

    following = set(t.friends.ids(screen_name=TWITTER_HANDLE)["ids"])
    followers = set(t.followers.ids(screen_name=TWITTER_HANDLE)["ids"])

    # put user IDs here that you want to keep following even if they don't
    # follow you back
    users_keep_following = set([])

    not_following_back = following - followers

    # make sure the "already followed" file exists
    if not os.path.isfile(ALREADY_FOLLOWED_FILE):
        with open(ALREADY_FOLLOWED_FILE, "w") as out_file:
            out_file.write("")

    # update the "already followed" file with users who didn't follow back
    already_followed = set(not_following_back)
    af_list = []
    with open(ALREADY_FOLLOWED_FILE) as in_file:
        for line in in_file:
            af_list.append(int(line))

    already_followed.update(set(af_list))
    del af_list

    with open(ALREADY_FOLLOWED_FILE, "w") as out_file:
        for val in already_followed:
            out_file.write(str(val) + "\n")

    for user_id in not_following_back:
        if user_id not in users_keep_following:
            t.friendships.destroy(user_id=user_id)
            print("unfollowed %d" % (user_id))


def auto_mute_following():
    """
        Mutes everyone that you are following
    """
    following = set(t.friends.ids(screen_name=TWITTER_HANDLE)["ids"])
    muted = set(t.mutes.users.ids(screen_name=TWITTER_HANDLE)["ids"])

    not_muted = following - muted

    # put user IDs of people you do not want to mute here
    users_keep_unmuted = set([])

    # mute all
    for user_id in not_muted:
        if user_id not in users_keep_unmuted:
            t.mutes.users.create(user_id=user_id)
            print("muted %d" % (user_id))


def auto_unmute():
    """
        Unmutes everyone that you have muted
    """
    muted = set(t.mutes.users.ids(screen_name=TWITTER_HANDLE)["ids"])

    # put user IDs of people you want to remain muted here
    users_keep_muted = set([])

    # mute all
    for user_id in muted:
        if user_id not in users_keep_muted:
            t.mutes.users.destroy(user_id=user_id)
            print("unmuted %d" % (user_id))


def is_ascii(s):
        return all(ord(c) < 128 for c in s)


def is_contained(s, l):
    return any(map(lambda e: s in e and s != e, l))


def distribute_follows_into_trends(count, trends):
    return map(lambda t: auto_follow(t, count=count/len(trends)), trends)


def strategy():
    # auto_unfollow_nonfollowers()
    # auto_mute_following()
    # auto_rt("phrase", count=1000)
    """
    countries = ['Worldwide', 'Argentina', 'Brazil', 'Chile', 'Spain',
                 'United States', 'Venezuela', 'United Kingdom',
                 'Dominican Republic', 'Ecuador', 'Panama']
    places = map(lambda p: p[u'woeid'], filter(lambda p: p['name'] in countries,
                                               t.trends.available()))
    trends = map(lambda p: t.trends.place(_id = p), places)
    """
    trends = [[{u'created_at': u'2015-05-02T13:59:24Z', u'trends': [{u'url': u'http://twitter.com/search?q=%23RoyalBaby', u'query': u'%23RoyalBaby', u'name': u'#RoyalBaby', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%2317YearsBattleOfHogwarts', u'query': u'%2317YearsBattleOfHogwarts', u'name': u'#17YearsBattleOfHogwarts', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23DemiWorldTourChina', u'query': u'%23DemiWorldTourChina', u'name': u'#DemiWorldTourChina', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Newcastle', u'query': u'Newcastle', u'name': u'Newcastle', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23MMKBrave44', u'query': u'%23MMKBrave44', u'name': u'#MMKBrave44', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23%D9%83%D9%84%D9%85%D8%A7%D8%AA_%D8%B3%D9%85%D8%B9%D8%AA%D9%87%D8%A7_%D9%85%D9%86_%D8%B4%D8%AE%D8%B5_%D8%AA%D8%AD%D8%A8%D9%87', u'query': u'%23%D9%83%D9%84%D9%85%D8%A7%D8%AA_%D8%B3%D9%85%D8%B9%D8%AA%D9%87%D8%A7_%D9%85%D9%86_%D8%B4%D8%AE%D8%B5_%D8%AA%D8%AD%D8%A8%D9%87', u'name': u'#\u0643\u0644\u0645\u0627\u062a_\u0633\u0645\u0639\u062a\u0647\u0627_\u0645\u0646_\u0634\u062e\u0635_\u062a\u062d\u0628\u0647', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22David+Beckham%22', u'query': u'%22David+Beckham%22', u'name': u'David Beckham', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Ruth+Rendell%22', u'query': u'%22Ruth+Rendell%22', u'name': u'Ruth Rendell', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Rio+Ferdinand%22', u'query': u'%22Rio+Ferdinand%22', u'name': u'Rio Ferdinand', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Derby', u'query': u'Derby', u'name': u'Derby', u'promoted_content': None}], u'as_of': u'2015-05-02T14:04:38Z', u'locations': [{u'woeid': 1, u'name': u'Worldwide'}]}], [{u'created_at': u'2015-05-02T13:59:24Z', u'trends': [{u'url': u'http://twitter.com/search?q=%23PintaCaraDeOrtoSi', u'query': u'%23PintaCaraDeOrtoSi', u'name': u'#PintaCaraDeOrtoSi', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23BuenSabado', u'query': u'%23BuenSabado', u'name': u'#BuenSabado', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23DiaDeLasTinistas', u'query': u'%23DiaDeLasTinistas', u'name': u'#DiaDeLasTinistas', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23QueOneMeGustaMas', u'query': u'%23QueOneMeGustaMas', u'name': u'#QueOneMeGustaMas', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23SabadoDeGanarSeguidores', u'query': u'%23SabadoDeGanarSeguidores', u'name': u'#SabadoDeGanarSeguidores', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Hungr%C3%ADa', u'query': u'Hungr%C3%ADa', u'name': u'Hungr\xeda', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22R%C3%ADo+Turbio%22', u'query': u'%22R%C3%ADo+Turbio%22', u'name': u'R\xedo Turbio', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Schwartzman', u'query': u'Schwartzman', u'name': u'Schwartzman', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Kate+Middleton%22', u'query': u'%22Kate+Middleton%22', u'name': u'Kate Middleton', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Jamaica', u'query': u'Jamaica', u'name': u'Jamaica', u'promoted_content': None}], u'as_of': u'2015-05-02T14:04:38Z', u'locations': [{u'woeid': 23424747, u'name': u'Argentina'}]}], [{u'created_at': u'2015-05-02T13:59:24Z', u'trends': [{u'url': u'http://twitter.com/search?q=%23DemiWorldTourChina', u'query': u'%23DemiWorldTourChina', u'name': u'#DemiWorldTourChina', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23VampireAttraction2015', u'query': u'%23VampireAttraction2015', u'name': u'#VampireAttraction2015', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%2317YearsBattleOfHogwarts', u'query': u'%2317YearsBattleOfHogwarts', u'name': u'#17YearsBattleOfHogwarts', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23TeAmoCu', u'query': u'%23TeAmoCu', u'name': u'#TeAmoCu', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23RoyalBaby', u'query': u'%23RoyalBaby', u'name': u'#RoyalBaby', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22David+Beckham%22', u'query': u'%22David+Beckham%22', u'name': u'David Beckham', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Kate+Middleton%22', u'query': u'%22Kate+Middleton%22', u'name': u'Kate Middleton', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Rio+Ferdinand%22', u'query': u'%22Rio+Ferdinand%22', u'name': u'Rio Ferdinand', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Championship', u'query': u'Championship', u'name': u'Championship', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Newcastle', u'query': u'Newcastle', u'name': u'Newcastle', u'promoted_content': None}], u'as_of': u'2015-05-02T14:04:38Z', u'locations': [{u'woeid': 23424768, u'name': u'Brazil'}]}], [{u'created_at': u'2015-05-02T13:59:24Z', u'trends': [{u'url': u'http://twitter.com/search?q=%22Ignacio+Walker%22', u'query': u'%22Ignacio+Walker%22', u'name': u'Ignacio Walker', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23FelizSabado', u'query': u'%23FelizSabado', u'name': u'#FelizSabado', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23InnovaRock', u'query': u'%23InnovaRock', u'name': u'#InnovaRock', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23RoyalBaby', u'query': u'%23RoyalBaby', u'name': u'#RoyalBaby', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Acapulco', u'query': u'Acapulco', u'name': u'Acapulco', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Pablo+Ot%C3%A1rola%22', u'query': u'%22Pablo+Ot%C3%A1rola%22', u'name': u'Pablo Ot\xe1rola', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Alsacia', u'query': u'Alsacia', u'name': u'Alsacia', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Valpara%C3%ADso+con+Santiago%22', u'query': u'%22Valpara%C3%ADso+con+Santiago%22', u'name': u'Valpara\xedso con Santiago', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Paraguay', u'query': u'Paraguay', u'name': u'Paraguay', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23ConfesionesNocturnas', u'query': u'%23ConfesionesNocturnas', u'name': u'#ConfesionesNocturnas', u'promoted_content': None}], u'as_of': u'2015-05-02T14:04:39Z', u'locations': [{u'woeid': 23424782, u'name': u'Chile'}]}], [{u'created_at': u'2015-05-02T13:59:30Z', u'trends': [{u'url': u'http://twitter.com/search?q=%23PtoPtaColora', u'query': u'%23PtoPtaColora', u'name': u'#PtoPtaColora', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Alex+Rodr%C3%ADguez%22', u'query': u'%22Alex+Rodr%C3%ADguez%22', u'name': u'Alex Rodr\xedguez', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23billboards2015', u'query': u'%23billboards2015', u'name': u'#billboards2015', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Constanza', u'query': u'Constanza', u'name': u'Constanza', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23LaPandillaPresiento', u'query': u'%23LaPandillaPresiento', u'name': u'#LaPandillaPresiento', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23DiaDelTrabajador', u'query': u'%23DiaDelTrabajador', u'name': u'#DiaDelTrabajador', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Alfa', u'query': u'Alfa', u'name': u'Alfa', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=romeo', u'query': u'romeo', u'name': u'romeo', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23MayweatherPacquiao', u'query': u'%23MayweatherPacquiao', u'name': u'#MayweatherPacquiao', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Yankees', u'query': u'Yankees', u'name': u'Yankees', u'promoted_content': None}], u'as_of': u'2015-05-02T14:04:39Z', u'locations': [{u'woeid': 23424800, u'name': u'Dominican Republic'}]}], [{u'created_at': u'2015-05-02T13:59:30Z', u'trends': [{u'url': u'http://twitter.com/search?q=%22LOS+ABUELOS%22', u'query': u'%22LOS+ABUELOS%22', u'name': u'LOS ABUELOS', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23EstamosEnMayoY', u'query': u'%23EstamosEnMayoY', u'name': u'#EstamosEnMayoY', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23TodasLasManosTodas', u'query': u'%23TodasLasManosTodas', u'name': u'#TodasLasManosTodas', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%2390a%C3%B1osdeIDOLATRIA', u'query': u'%2390a%C3%B1osdeIDOLATRIA', u'name': u'#90a\xf1osdeIDOLATRIA', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23FeriadoSeguro', u'query': u'%23FeriadoSeguro', u'name': u'#FeriadoSeguro', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23EcuadorNeeds5SOS', u'query': u'%23EcuadorNeeds5SOS', u'name': u'#EcuadorNeeds5SOS', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22plaza+de+santo+domingo%22', u'query': u'%22plaza+de+santo+domingo%22', u'name': u'plaza de santo domingo', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22India+Mar%C3%ADa%22', u'query': u'%22India+Mar%C3%ADa%22', u'name': u'India Mar\xeda', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Barcelona+Sporting+Club%22', u'query': u'%22Barcelona+Sporting+Club%22', u'name': u'Barcelona Sporting Club', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Avengers', u'query': u'Avengers', u'name': u'Avengers', u'promoted_content': None}], u'as_of': u'2015-05-02T14:04:39Z', u'locations': [{u'woeid': 23424801, u'name': u'Ecuador'}]}], [{u'created_at': u'2015-05-02T13:59:34Z', u'trends': [{u'url': u'http://twitter.com/search?q=Metro', u'query': u'Metro', u'name': u'Metro', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23BeisbolMayor2015', u'query': u'%23BeisbolMayor2015', u'name': u'#BeisbolMayor2015', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23TomorrowlandBrasil2015', u'query': u'%23TomorrowlandBrasil2015', u'name': u'#TomorrowlandBrasil2015', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23FelizDiaDelTrabajador', u'query': u'%23FelizDiaDelTrabajador', u'name': u'#FelizDiaDelTrabajador', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23YoS6yAvenger', u'query': u'%23YoS6yAvenger', u'name': u'#YoS6yAvenger', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23billboards2015', u'query': u'%23billboards2015', u'name': u'#billboards2015', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Pacquiao', u'query': u'Pacquiao', u'name': u'Pacquiao', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22feliz+d%C3%ADa+del+trabajo%22', u'query': u'%22feliz+d%C3%ADa+del+trabajo%22', u'name': u'feliz d\xeda del trabajo', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Isla+Col%C3%B3n%22', u'query': u'%22Isla+Col%C3%B3n%22', u'name': u'Isla Col\xf3n', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=capira', u'query': u'capira', u'name': u'capira', u'promoted_content': None}], u'as_of': u'2015-05-02T14:04:40Z', u'locations': [{u'woeid': 23424924, u'name': u'Panama'}]}], [{u'created_at': u'2015-05-02T13:59:24Z', u'trends': [{u'url': u'http://twitter.com/search?q=%232deMayo', u'query': u'%232deMayo', u'name': u'#2deMayo', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23NuncaDejesDeSonreirAM', u'query': u'%23NuncaDejesDeSonreirAM', u'name': u'#NuncaDejesDeSonreirAM', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23N1CanalFiesta18', u'query': u'%23N1CanalFiesta18', u'name': u'#N1CanalFiesta18', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23RoyalBaby', u'query': u'%23RoyalBaby', u'name': u'#RoyalBaby', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23PerfectHour', u'query': u'%23PerfectHour', u'name': u'#PerfectHour', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Newcastle', u'query': u'Newcastle', u'name': u'Newcastle', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Derby', u'query': u'Derby', u'name': u'Derby', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22David+Beckham%22', u'query': u'%22David+Beckham%22', u'name': u'David Beckham', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Championship', u'query': u'Championship', u'name': u'Championship', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Rio+Ferdinand%22', u'query': u'%22Rio+Ferdinand%22', u'name': u'Rio Ferdinand', u'promoted_content': None}], u'as_of': u'2015-05-02T14:04:40Z', u'locations': [{u'woeid': 23424950, u'name': u'Spain'}]}], [{u'created_at': u'2015-05-02T13:59:24Z', u'trends': [{u'url': u'http://twitter.com/search?q=%23RoyalBaby', u'query': u'%23RoyalBaby', u'name': u'#RoyalBaby', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23nufc', u'query': u'%23nufc', u'name': u'#nufc', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Derby', u'query': u'Derby', u'name': u'Derby', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Blackpool', u'query': u'Blackpool', u'name': u'Blackpool', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Championship', u'query': u'Championship', u'name': u'Championship', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Ruth+Rendell%22', u'query': u'%22Ruth+Rendell%22', u'name': u'Ruth Rendell', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Brentford', u'query': u'Brentford', u'name': u'Brentford', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23PerfectHour', u'query': u'%23PerfectHour', u'name': u'#PerfectHour', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Rio+Ferdinand%22', u'query': u'%22Rio+Ferdinand%22', u'name': u'Rio Ferdinand', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23dcfc', u'query': u'%23dcfc', u'name': u'#dcfc', u'promoted_content': None}], u'as_of': u'2015-05-02T14:04:41Z', u'locations': [{u'woeid': 23424975, u'name': u'United Kingdom'}]}], [{u'created_at': u'2015-05-02T13:59:24Z', u'trends': [{u'url': u'http://twitter.com/search?q=%23RoyalBaby', u'query': u'%23RoyalBaby', u'name': u'#RoyalBaby', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23FreeComicBookDay', u'query': u'%23FreeComicBookDay', u'name': u'#FreeComicBookDay', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23uppers', u'query': u'%23uppers', u'name': u'#uppers', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=Newcastle', u'query': u'Newcastle', u'name': u'Newcastle', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23IndyMini', u'query': u'%23IndyMini', u'name': u'#IndyMini', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23satchat', u'query': u'%23satchat', u'name': u'#satchat', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Kate+Middleton%22', u'query': u'%22Kate+Middleton%22', u'name': u'Kate Middleton', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22David+Beckham%22', u'query': u'%22David+Beckham%22', u'name': u'David Beckham', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Ruth+Rendell%22', u'query': u'%22Ruth+Rendell%22', u'name': u'Ruth Rendell', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Duchess+of+Cambridge%22', u'query': u'%22Duchess+of+Cambridge%22', u'name': u'Duchess of Cambridge', u'promoted_content': None}], u'as_of': u'2015-05-02T14:04:41Z', u'locations': [{u'woeid': 23424977, u'name': u'United States'}]}], [{u'created_at': u'2015-05-02T13:59:24Z', u'trends': [{u'url': u'http://twitter.com/search?q=%23LiberenARosmit', u'query': u'%23LiberenARosmit', u'name': u'#LiberenARosmit', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23SabadoDeGanarSeguidores', u'query': u'%23SabadoDeGanarSeguidores', u'name': u'#SabadoDeGanarSeguidores', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23SocialismoEsJusticia', u'query': u'%23SocialismoEsJusticia', u'name': u'#SocialismoEsJusticia', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Feliz+S%C3%A1bado%22', u'query': u'%22Feliz+S%C3%A1bado%22', u'name': u'Feliz S\xe1bado', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23RoyalBaby', u'query': u'%23RoyalBaby', u'name': u'#RoyalBaby', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%23UNAMUJER', u'query': u'%23UNAMUJER', u'name': u'#UNAMUJER', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Kate+Middleton%22', u'query': u'%22Kate+Middleton%22', u'name': u'Kate Middleton', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Atanasio+Girardot%22', u'query': u'%22Atanasio+Girardot%22', u'name': u'Atanasio Girardot', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22David+Beckham%22', u'query': u'%22David+Beckham%22', u'name': u'David Beckham', u'promoted_content': None}, {u'url': u'http://twitter.com/search?q=%22Pelea+del+Siglo%22', u'query': u'%22Pelea+del+Siglo%22', u'name': u'Pelea del Siglo', u'promoted_content': None}], u'as_of': u'2015-05-02T14:04:41Z', u'locations': [{u'woeid': 23424982, u'name': u'Venezuela'}]}]]
    trends = map(lambda t: filter(lambda h: not h['promoted_content'],
                                  t[0]['trends']), trends)
    trends = map(lambda t: map(lambda h: h['name'], t), trends)
    trends = set(filter(is_ascii,
                        itertools.chain(*trends)))
    hights = filter(lambda t: is_contained(t, trends), trends)
    trends = list(trends - set(hights))
    distribute_follows_into_trends(100, hights)
    selected = map(lambda i: trends[i], random.sample(xrange(len(trends)), 10))
    distribute_follows_into_trends(100, selected)


if __name__ == "__main__":
    try:
        strategy()
    except Exception, e:
        print e
