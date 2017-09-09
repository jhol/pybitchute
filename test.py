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

import requests

USERNAME = ''
PASSWORD = ''

protocol = 'https'
host = 'www.bitchute.com'
server = protocol + '://' + host

session = requests.Session()
session.get(server + '/')
csrftoken = session.cookies['csrftoken']

r = session.post(server + '/accounts/login/',
    data={
        'username': USERNAME, 
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrftoken},
    headers={'Referer': server + '/'})

if r.json()['success'] != True:
    raise RuntimeError('Login failed')
