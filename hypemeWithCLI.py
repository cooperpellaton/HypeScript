import unicodedata
from time import time
import urllib2
import urllib
from bs4 import BeautifulSoup
import json
import string
import os
import sys


HYPEM_URL = sys.argv = raw_input('Enter link to track: ')
NUMBER_OF_PAGES = 1

DEBUG = False

validFilenameChars = '-_.() %s%s' % (string.ascii_letters, string.digits)


def removeDisallowedFilenameChars(filename):
    cleanedFilename = unicodedata.normalize(
        'NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleanedFilename if c in validFilenameChars)


class HypeScraper:

    def __init__(self):
        pass

    def start(self):
        print '--------STARTING DOWNLOAD--------'
        print '\tURL : {} '.format(HYPEM_URL)

        for i in range(1, NUMBER_OF_PAGES + 1):

            page_url = HYPEM_URL + '/{}'.format(i)
            html, cookie = self.get_html_file(page_url)

            if DEBUG:
                html_file = open('hypeHTML.html', 'w')
                html_file.write(html)
                html_file.close()

            tracks = self.parse_html(html)

            self.download_songs(tracks, cookie)

    def get_html_file(self, url):
        data = {'ax': 1, 'ts': time()}
        data_encoded = urllib.urlencode(data)
        complete_url = url + '?{}'.format(data_encoded)
        request = urllib2.Request(complete_url)
        response = urllib2.urlopen(request)
        # save our cookie
        cookie = response.headers.get('Set-Cookie')
        # grab the HTML
        html = response.read()
        response.close()
        return html, cookie

    def parse_html(self, html):
        track_list = []
        soup = BeautifulSoup(html)
        html_tracks = soup.find(id='displayList-data')
        if html_tracks is None:
            return track_list
        try:
            track_list = json.loads(html_tracks.text)
            if DEBUG:
                print json.dumps(track_list, sort_keys=True, indent=4,
                                 separators=(',', ': '))
            return track_list[u'tracks']
        except ValueError:
            print 'Hypemachine contained invalid JSON.'
            return track_list

    # tracks have id, title, artist, key
    def download_songs(self, tracks, cookie):

        print '\tDOWNLOADING SONG...'
        for track in tracks:

            key = track[u'key']
            id = track[u'id']
            artist = removeDisallowedFilenameChars(track[u'artist'])
            title = removeDisallowedFilenameChars(track[u'song'])
            type = track[u'type']

            print u'\t{} by {}'.format(title, artist)
            print ' _______  _______  _______  _______  _______  _______  ______  '
            print '(  ____ \(  ____ \(  ____ )(  ___  )(  ____ )(  ____ \(  __  \ '
            print '| (    \/| (    \/| (    )|| (   ) || (    )|| (    \/| (  \  )'
            print '| (_____ | |      | (____)|| (___) || (____)|| (__    | |   ) |'
            print '(_____  )| |      |     __)|  ___  ||  _____)|  __)   | |   | |'
            print '      ) || |      | (\ (   | (   ) || (      | (      | |   ) |'
            print '/\____) || (____/\| ) \ \__| )   ( || )      | (____/\| (__/  )'
            print '\_______)(_______/|/   \__/|/     \||/       (_______/(______/ '

            if type is False:
                print '\tSKIPPING SONG SINCE NO LONGER AVAILABLE...'
                continue

            try:
                serve_url = 'http://hypem.com/serve/source/{}/{}'.format(id,
                                                                         key)
                request = urllib2.Request(serve_url, '', {'Content-Type':
                                                          'application/json'})
                request.add_header('cookie', cookie)
                response = urllib2.urlopen(request)
                song_data_json = response.read()
                response.close()
                song_data = json.loads(song_data_json)
                url = song_data[u'url']

                download_response = urllib2.urlopen(url)
                filename = '{} - {}.mp3'.format(artist, title)
                if os.path.exists(filename):
                    print('File already exists , skipping')
                else:
                    mp3_song_file = open(filename, 'wb')
                    mp3_song_file.write(download_response.read())
                    mp3_song_file.close()
            except urllib2.HTTPError, e:
                print('HTTPError = ' + str(e.code) +
                      ' trying hypem download url.')
            except urllib2.URLError, e:
                print('URLError = ' + str(e.reason) +
                      ' trying hypem download url.')
            except Exception, e:
                print 'generic exception: ' + str(e)


def main():
    scraper = HypeScraper()
    scraper.start()

if __name__ == '__main__':
    main()
