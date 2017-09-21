#!/usr/bin/env python3
##
## This file is part of the pybitchute project.
##
## Copyright (C) 2017 Joel Holdsworth <joel@airwebreathe.org.uk>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##

import re
import requests

username = ''
password = ''

channel = ''
title = ''
description = ''

protocol = 'https'
domain = 'bitchute.com'
www_server = '{0}://www.{1}'.format(protocol, domain)

def upload(username, password, channel, title, description, video_path, thumbnail_path):
    session = requests.Session()

    csrftoken = session.get(www_server + '/').cookies['csrftoken']

    r = session.post(www_server + '/accounts/login/',
        data={
            'username': username,
            'password': password,
            'csrfmiddlewaretoken': csrftoken
        },
        headers={'referer': www_server + '/'})

    if r.json()['success'] != True:
        raise RuntimeError('Login failed')

    r = session.get('{0}/channel/{1}/'.format(www_server, channel))
    if r.status_code != 200:
        raise RuntimeError('Failed to get channel profile page')
    m = re.search('/channel/([A-Za-z0-9]+)/upload/', r.text)
    if not m:
        raise RuntimeError('Couldn\'t find channel code')
    cdid = m.group(1)

    r = session.get('{0}/channel/{1}/upload/?'.format(www_server, cdid))
    upload_url = r.url
    upload_server = '/'.join(r.url.split('/')[0:3])
    query_string = {k:v for k, v in [kv.split('=') for kv in r.url.split('?')[1].split('&')]}
    upload_code = query_string['upload_code']
    cid = query_string['cid']

    m = re.search("name='csrfmiddlewaretoken' value='([A-Za-z0-9]+)'", r.text)
    if not m:
        raise RuntimeError('Couldn\'t find csrfmiddlewaretoken')
    csrfmiddlewaretoken = m.group(1)

    r = session.post(upload_server + '/videos/uploadmeta/',
        data={
            'upload_title': title,
            'upload_description': description,
            'upload_code': upload_code,
            'csrfmiddlewaretoken': csrfmiddlewaretoken
        },
        headers={'referer': upload_url})

    if r.status_code != 200:
        raise RuntimeError('Upload of title and description failed')

    def _post_file(file, type, mime_type):
        return session.post(upload_server + '/videos/upload/',
            data={
                'upload_type': type,
                'upload_code': upload_code,
                'csrfmiddlewaretoken': csrfmiddlewaretoken
            },
            files={
                'file': (file, open(file, 'rb'), mime_type)
            },
            headers={'referer': upload_url})

    print('Upload video...')
    r = _post_file(video_path, 'video', 'video/mp4')
    if r.status_code != 200:
        raise RuntimeError('Upload of video failed')

    print('Upload thumbnail...')
    r = _post_file(thumbnail_path, 'image', 'image/jpeg')
    if r.status_code != 200:
        raise RuntimeError('Upload of thumbnail failed')

    print('Finish upload...')
    r = session.post(upload_server + '/videos/finish_upload/',
            params={
                'cdid': cdid,
                'channel': channel,
                'cid': cid,
                'upload_code': upload_code,
            },
            data={
                'csrfmiddlewaretoken': csrfmiddlewaretoken
            },
            headers={'referer': upload_url})

    if r.status_code != 200:
        raise RuntimeError('Failed to finish submission')

    print(r.url)


upload(username=username, password=password, channel=channel, title=title, description=description,
    video_path='test.mp4', thumbnail_path='test.jpg')
