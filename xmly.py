import sys, json, traceback
from bs4 import BeautifulSoup
from datetime import *
from urlparse import urlparse

from pyvin.spider import Spider, Persist, SpiderSoup
from pyvin.core import Log

class XMLY:
    '''
    album url like: http://www.ximalaya.com/35878101/album/3475911
    '''

    BASE_URL = 'http://www.ximalaya.com'
    TRACK_URL = 'http://www.ximalaya.com/tracks/%s.json'

    def __init__(self, url):
        self.TAG = XMLY.__name__

        self.callbacks = {
                '^http://www.ximalaya.com/[0-9]{1,8}/album/[0-9]{1,7}': self.find_sound_list,
                '^http://www.ximalaya.com/[0-9]{1,8}/sound/[0-9]{1,8}': self.find_sound_url,
                '^http://www.ximalaya.com/tracks/[0-9]{1,8}.json':self.find_sound_url_json
        }

        self.album_url = url

        self.spider = Spider('XMLY')
        self.spider.set_proxy('proxy-amer.delphiauto.net:8080', 'rzfwch', '8ik,.lo9')
        self.spider.add_callbacks(self.callbacks)
        self.spider.add_urls([self.album_url])
        self.spider.start()

    def find_sound_list(self, url, response):
        try:
            self.soup = BeautifulSoup(response, "html5lib")
            soundlist = self.soup.find('div', attrs={'class':'album_soundlist'})
            soundlist = soundlist.findAll('a', attrs={'class':'title'})
            # print soundlist
            for i, a in enumerate(soundlist):
                sound_url = a['href']
                sound_title = a['title']
                track_id = sound_url[sound_url.rfind('/') + 1:]
                track_url = XMLY.TRACK_URL % track_id
                # print '%02d, %s, %s' % (i, sound_title, track_url)
                self.spider.add_urls([track_url])
        except:
            traceback.print_exc()

    def find_sound_url(self, url, response):
        '''
        http://www.ximalaya.com/35878101/sound/27570896
        not used now
        '''
        self.soup = BeautifulSoup(response, "html5lib")
        elapsed_time = self.soup.find('span', attrs={'class':'time fr'})
        elapsed_time = elapsed_time.text
        print 'time: %s' % elapsed_time

    def find_sound_url_json(self, url, response):
        '''http://www.ximalaya.com/tracks/27570896.json'''
        track_obj = json.loads(response)
        print track_obj['play_path']
        self.spider.fetch.wget(track_obj['play_path'], track_obj['title'])

if __name__ == "__main__":
    # print sys.argv[1]
    url = sys.argv[1]
    xmly = XMLY(url)
