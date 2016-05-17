import os
import sys
import urllib2
import base64
from xml.dom import minidom

class VLC:
    class XML:
        def __init__(self, file):
            self.file = file
            self.xmldoc = minidom.parseString(file)

        def get_element_by_tag_name(self, name):
            return self.xmldoc.getElementsByTagName(name)

        def create_playlist_item(self, xml_item):
            return VLC.PlaylistItem(
                xml_item.attributes['duration'].value,
                xml_item.attributes['id'].value,
                xml_item.attributes['name'].value,
                xml_item.attributes['ro'].value,
                xml_item.attributes['uri'].value,
            )

        def create_status_item(self, xml_item):

            return VLC.Status(
                xml_item.attributes['fullscreen'].value,
                xml_item.attributes['aspect_ratio'].value,
                xml_item.attributes['audio_delay'].value,
                xml_item.attributes['api_version'].value,
                xml_item.attributes['time'].value,
                xml_item.attributes['volume'].value,
                xml_item.attributes['length'].value,
                xml_item.attributes['random'].value,
                xml_item.attributes['state'].value,
                xml_item.attributes['loop'].value,
                xml_item.attributes['position'].value,
                xml_item.attributes['repeat'].value,
            )

    class Status:
        def __init__(self, fullscreen, aspect_ratio, audio_delay, api_version,
                     time, volume, length, random, state, loop, position, repeat):
            self.fullscreen = fullscreen
            self.aspect_ratio = aspect_ratio
            self.audio_delay = audio_delay
            self.api_version = api_version
            self.time = time
            self.volume = volume
            self.length = length
            self.random = random
            self.state = state
            self.loop = loop
            self.position = position
            self.repeat = repeat

    class PlaylistItem:
        def __init__(self, duration, id, name, ro, uri):
            self.duration = duration
            self.id = id
            self.name = name
            self.ro = ro
            self.uri = uri

        def __str__(self):
            return ''.join([
                'id : ', self.id,
                ' name : ', self.name,
                ' duration : ', self.duration,
                ' uri : ', self.uri
            ])

        def __getitem__(self, item):
            if item=='duration':
                return self.duration
            if item=='id':
                return self.id
            if item=='name':
                return self.name
            if item=='ro':
                return self.ro
            if item=='uri' or item=='url':
                return self.uri
            assert False, 'Invalid item key'

    def __init__(self, base_url='127.0.0.1', port=8080, username='', password='godfather'):
        if 'http:' not in base_url:
            base_url = 'http://'+base_url
        self.base_url = base_url
        self.port = port
        self.server_url = self.base_url + ':' + str(self.port) + '/'
        self.username = username
        self.password = password
        self.is_random = False
        status = self.status()

    def get_auth_header(self):
        return base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')

    def request(self, r):
        request = urllib2.Request(''.join([ self.server_url,'requests/',r]))
        request.add_header("Authorization", "Basic %s" % self.get_auth_header())
        return urllib2.urlopen(request).read()

    def status(self):
        xml = VLC.XML(self.request('status.xml'))
        return xml.create_status_item(xml.get_element_by_tag_name('root'))

    def playlist(self):
        return self.request('playlist.xml')

    def cmd(self, c):
        return self.request(''.join(['status.xml?command=', c]))

    def stop(self):
        return self.cmd('pl_stop')

    def play(self):
        return self.cmd('pl_play')

    def pause(self):
        return self.cmd('pl_pause')

    def next(self):
        return self.cmd('pl_next')

    def prev(self):
        return self.cmd('pl_previous')

    def empty(self):
        return self.cmd('pl_empty')

    def rm_from_playlist(self, id):
        return self.cmd(''.join(['pl_delete&id=', str(id)]))

    def random(self):
        return self.cmd('pl_random')

    def get_playlist_items(self):
        xml = VLC.XML(self.playlist())
        items = xml.get_element_by_tag_name('leaf')
        return [xml.create_playlist_item(i) for i in items]

def main(argv):
    vlc = VLC()
    print vlc.status()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
