# -*- encoding: utf-8 -*-

import httplib2
import json
import traceback
import urllib
import web
from datetime import datetime, timedelta

from troll.security import db

class AuthGoogle(object):

    _auth_uri = 'https://accounts.google.com/o/oauth2/auth'
    _scope_uri = 'https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email'

    def __init__(self, conf):
        self._client_id = conf['client_id']
        self._client_secret = conf['client_secret']
        self._redirect_uri = conf['redirect_uri']

    def authenticate(self, app):
        i = web.input()
        if 'code' in i:
            try:
                token = self._getToken(i['code'])
                auth = db.AuthGoogle({
                    'access_token': token['access_token'],
                    'refresh_token': token['refresh_token'],
                    'expiration_date': datetime.utcnow() + timedelta(seconds=int(token['expires_in'])),
                    'token_type': token['token_type'],
                })
                user = self._getUser(auth)
                return auth, user
            except Exception, e:
                traceback.print_exc()
                print "ERROR: Cannot get google tokens:", e
                return None
        elif 'error' in i:
            return None
        else:
            req = urllib.urlencode({
                'client_id': self._client_id,
                'redirect_uri': self._redirect_uri,
                'scope': self._scope_uri,
                'response_type': 'code',
            })
            raise web.seeother(self._auth_uri + '?' + req)

    def _getToken(self, code):
        url = "https://accounts.google.com/o/oauth2/token"
        data = {
            'code': code,
            'client_id': self._client_id,
            'client_secret': self._client_secret,
            'redirect_uri': self._redirect_uri,
            'grant_type': 'authorization_code',
        }
        client = httplib2.Http()
        body = urllib.urlencode(data)
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response, content = client.request(url, 'POST', body=body, headers=headers)
        token = json.loads(content)
        assert 'access_token' in token
        assert 'refresh_token' in token
        assert 'token_type' in token
        assert 'expires_in' in token
        return token

    def _getUserMail(self, auth):
        url = "https://www.googleapis.com/userinfo/email?alt=json"
        headers = {
            'Authorization': auth.token_type + ' ' + auth.access_token,
        }
        client = httplib2.Http()
        response, content = client.request(url, 'GET', headers=headers)
        data = json.loads(content)['data']
        if ('is_verified' in data and data['is_verified']) or \
           ('isVerified' in data and data['isVerified']):
            return data['email']

    def _getUser(self, auth):
        url = 'https://www.googleapis.com/plus/v1/people/me'
        headers = {
            'Authorization': auth.token_type + ' ' + auth.access_token,
        }
        client = httplib2.Http()
        response, content = client.request(url, 'GET', headers=headers)
        user_infos = json.loads(content)
        fullname = user_infos['displayName']
        mail = None
        if 'emails' in user_infos:
            for m in user_infos['emails']:
                if mail is None or m['primary']:
                    mail = m['value']
        else:
            mail = self._getUserMail(auth)
        assert mail is not None
        return db.User({
            'mail': mail,
            'fullname': fullname,
            'role_id': 'user',
            'auth_type': 'google',
            'meta': content.decode('utf-8'),
        })


