#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import time
import traceback
import platform

from HTMLParser import HTMLParser
import requests
import xmltodict

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def notify_wrapper(title, subtitle, url):
    if platform.system() == 'Linux':
        from gi.repository import Notify
        Notify.init("Subreddit Monitor")
        notification = Notify.Notification.new(title,
                                                subtitle)
        notification.show()
        Notify.uninit()
    if platform.system() == 'Darwin':
        from pync import Notifier
        Notifier.notify(title,
                        title=subtitle,
                        open=url)
        Notifier.remove(os.getpid())
        Notifier.list(os.getpid())
    else:
        print("You appear to be using an unsupported OS.")

if __name__ == "__main__":

    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # id_path = os.path.join(current_dir, "newest_id.txt")
    #
    # current_id = None
    # try:
    #     with open(id_path, 'r') as f:
    #         current_id = f.read()
    # except:
    #     pass
    while True:

        subreddits = ['python', 'worldnews', 'relationships', 'iama']
        for subreddit in subreddits:
            url = "https://www.reddit.com/r/{}/new/.rss".format(subreddit)
            headers = {'User-Agent': 'Mozilla/5.0'}

            try:
                response = requests.get(url, headers=headers)
                rss = xmltodict.parse(response.text)

                newest_entry = rss['feed']['entry'][0]
                timestamp = newest_entry['updated']
                newest_id = newest_entry['id']
                entry_url = newest_entry['link']['@href']
                content = strip_tags(newest_entry['content']['#text'])
                title = strip_tags(newest_entry['title'])

                #if current_id != newest_id:
                current_id = newest_id
                notify_wrapper(title, content[:100], entry_url)

                #with open(id_path, 'w') as f:
                #    f.write(current_id)

            except Exception as e:
                traceback.print_exc()
                try:
                    print(response.status_code)
                    print(response.text)
                except:
                    pass
            finally:
                time.sleep(60 * 0.25)
