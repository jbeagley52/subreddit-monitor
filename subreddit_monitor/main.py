#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time
import traceback
import platform

from pprint import pprint
import requests
import xmltodict

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

    current_dir = os.path.dirname(os.path.abspath(__file__))
    id_path = os.path.join(current_dir, "newest_id.txt")

    current_id = None
    try:
        with open(id_path, 'r') as f:
            current_id = f.read()
    except:
        pass

    subreddit = "python"
    url = "https://www.reddit.com/r/{}/new/.rss".format(subreddit)
    headers = {'User-Agent': 'Mozilla/5.0'}

    while True:
        try:
            response = requests.get(url, headers=headers)
            #print(response.text)
            rss = xmltodict.parse(response.text)

            newest_entry = rss['feed']['entry'][0]
            print(newest_entry)
            timestamp = newest_entry['updated']
            newest_id = newest_entry['id']
            entry_url = newest_entry['link']['@href']
            content = newest_entry['content']['#text']
            title = newest_entry['title']

            if current_id != newest_id:
                current_id = newest_id
                notify_wrapper(title, content[:100], entry_url)

                #print("{} : {}".format(title[:40], current_id))
                with open(id_path, 'w') as f:
                    f.write(current_id)

        except Exception as e:
            traceback.print_exc()
            try:
                print(response.status_code)
                print(response.text)
            except:
                pass
        finally:
            time.sleep(60 * 5)
