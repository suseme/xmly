import sys, json, traceback, os
from bs4 import BeautifulSoup
from datetime import *
from urlparse import urlsplit

from pyvin.spider import Spider

class XMLY:
    '''
    album url like: http://www.ximalaya.com/35878101/album/3475911
    '''

    BASE_URL = 'http://www.ximalaya.com'
    TRACK_URL = 'http://www.ximalaya.com/tracks/%s.json'

    def __init__(self, url):
        self.TAG = XMLY.__name__

        self.starts = [
            url,
        ]

        self.callbacks = {
                '^http://www.ximalaya.com/[0-9]{1,8}/album/[0-9]{1,7}': self.find_sound_list,
                '^http://www.ximalaya.com/[0-9]{1,8}/sound/[0-9]{1,8}': self.find_sound_url,
                '^http://www.ximalaya.com/tracks/[0-9]{1,8}.json':self.find_sound_url_json
        }

        self.spider = Spider('XMLY')
        # self.spider.set_proxy('server:8080', 'user', 'password')
        self.spider.add_callbacks(self.callbacks)
        self.spider.add_urls(self.starts)
        self.spider.set_max_thread(10)
        # self.spider.start()

    def start(self):
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
        try:
            track_obj = json.loads(response)
            url = track_obj['play_path']
            title = track_obj['title']
            album = track_obj['album_title']
            self.download(url, title, album)
        except:
            traceback.print_exc()

    def download(self, url, track_name, album_name):
        scheme, netloc, path, query, fragment = urlsplit(url)
        filename = os.path.basename(path)
        filename, extname = os.path.splitext(filename)
        path = os.path.join(album_name, '%s%s' % (track_name, extname))
        self.spider.download(url, path)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        xmly = XMLY(sys.argv[1])
        xmly.start()
    else:
        print '%s album_url' % sys.argv[0]
