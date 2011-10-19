# -*- encoding: utf-8 -*-

import cgi
from datetime import datetime, timedelta
import httplib2
import json
import traceback
import urllib
import web

from troll.security import db

class AuthFacebook(object):

    _client_auth_uri = 'https://www.facebook.com/dialog/oauth'
    _auth_uri = 'https://graph.facebook.com/oauth/access_token'

    def __init__(self, conf):
        self._redirect_uri = conf['redirect_uri']
        self._client_id = conf['client_id']
        self._client_secret = conf['client_secret']

    def authenticate(self, app):
        i = web.input()
        if 'code' in i:
            code = i['code']
            try:
                access_token, expires = self._getToken(code)
                auth = db.AuthFacebook({
                    'access_token': access_token,
                    'expiration_date': datetime.utcnow() + timedelta(seconds=int(expires)),
                })
                user = self._getUser(auth)
                return auth, user
            except Exception, e:
                traceback.print_exc()
                print "ERROR: Cannot authenticate with Facebook:", e
                return None
        elif 'error' in i:
            return None
        else:
            req = urllib.urlencode({
                'client_id': self._client_id,
                'redirect_uri': self._redirect_uri,
                'scope': 'email',
            })
            raise web.seeother(self._client_auth_uri + '?' + req)

    def _getToken(self, code):
        req = urllib.urlencode({
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'redirect_uri': self._redirect_uri,
            'code': code,
        })
        url = self._auth_uri + '?' + req
        client = httplib2.Http()
        response, content = client.request(url, 'GET')
        token = cgi.parse_qs(content)
        return token['access_token'][0], token['expires'][0]

    def _getUser(self, auth):
        req = urllib.urlencode({
            'access_token': auth.access_token,
        })
        url = "https://graph.facebook.com/me?" + req
        client = httplib2.Http()
        response, content = client.request(url, 'GET')
        data = json.loads(content)
        return db.User({
            'mail': data['email'],
            'fullname': data['name'],
            'auth_type': 'facebook',
            'role_id': 'user',
            'meta': content.decode('utf-8'),
        })

