# -*- coding: utf-8 -*-

import os
import re
import sqlite3
import logging
from urllib.parse import urlparse

import vk
import requests

from .sql_queries import SQL
from .conf import APP_ID, SCOPE


class VKSyncManager(object):

    def __init__(self):
        self.get_paths()
        self.connect_db()
        self.init_logger()

    def get_paths(self):
        """ Application's configs and database paths """

        xch = os.getenv('XDG_CONFIG_HOME')
        if xch:
            self.conf_path = os.path.join(xch, 'vkasync')
        else:
            self.conf_path = os.path.join(
                os.path.expanduser('~'), '.config', 'vkasync'
            )

        if not os.path.exists(self.conf_path):
            os.makedirs(self.conf_path)

        self.db_path = os.path.join(self.conf_path, 'db.sqlite')

    def connect_db(self):
        """ Open database and create cursor """

        db_exists = os.path.exists(self.db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Create table with users access tokens
        if not db_exists:
            self.cursor.execute(SQL['create_users_table'])
            self.conn.commit()

    def disconnect(self):
        """ Close database """

        self.conn.close()

    def init_logger(self):
        """ Create logger for vkasync module """

        self.logger = logging.getLogger('vkasync')
        self.log_path = os.path.join(self.conf_path, 'vkasync.log')

        file_handler = logging.FileHandler(self.log_path)
        file_handler.setLevel(logging.ERROR)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def create_token(self, login, passwd):
        """ Create new access_token with login and password """

        try:
            session = vk.AuthSession(app_id=APP_ID, scope=SCOPE,
                                     user_login=login, user_password=passwd)
            api = vk.API(session)
            token = api._session.access_token

        except vk.api.VkAuthError:
            self.logger.error('Auth error with password for %s' % login)
            token = None

        return token

    def add_login(self, login, passwd):
        """ Add new login with access token to database """

        token = self.create_token(login, passwd)
        if token is None:
            return

        # Add new token to database
        self.cursor.execute(SQL['add_token'], (login, token))
        self.conn.commit()

        return True

    def check_login(self, login):
        """ Check does login exists in database """

        self.cursor.execute(SQL['get_token'], (login,))
        # If login in table, len of res will > 0
        res = self.cursor.fetchall()

        return len(res) > 0

    def rm_login(self, login):
        """ Remove login from database """

        self.cursor.execute(SQL['rm_token'], (login,))
        self.conn.commit()

    def open_vksession(self, login):
        """ Open VK API session """

        self.cursor.execute(SQL['get_token'], (login,))
        token = self.cursor.fetchall()[0][0]

        try:
            self.session = vk.Session(access_token=token)
            self.vkapi = vk.API(self.session)
            return True

        except vk.api.VkAuthError:
            self.logger.error(
                'Auth error with access_token for %s' % login
            )

    def get_audios(self, owner_id, save_path=None, rm_audio=False,
                   rewrite=False):
        """ Get audios list and save them to disk """

        errors = 0
        pattern = '[^\w\s\-\.\(\)\[\]]'

        if save_path is None:
            save_path = os.path.join(os.path.expanduser('~'), 'vkasync')

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        audios = self.vkapi.audio.get(owner_id=owner_id)
        for audio in audios[1:]:  # audios[0] == count
            _track = '%s - %s' % (audio['artist'], audio['title'])
            track = re.sub(pattern, '_', _track)

            # URL without ?extra=
            url_parse = urlparse(audio['url'])
            url = url_parse._replace(query=None).geturl()

            ext = os.path.splitext(os.path.split(url)[1])[1]
            track_path = os.path.join(save_path, '%s%s' % (track, ext))

            if (not os.path.exists(track_path)) or rewrite:
                res = self.download_file(url, track_path, _track)

                if not res:
                    errors += 1
                else:
                    # TODO: remove audio
                    if rm_audio:
                        pass

        return errors

    def download_file(self, url, file_path, track_name):
        """ Download and save file """

        req = requests.get(url, stream=True)
        if req.status_code != 200:
            err_msg = 'track: %s, url: %s, status code %d'
            self.logger.error(err_msg % (track_name, url, req.status_code))
            return False

        with open(file_path, 'wb') as f:
            for chunk in req.iter_content(1024):
                f.write(chunk)

        return True

    def name2id(self, page_name, group_page=False):
        """ Convert vk page name to uid / gid """

        if page_name.startswith('-'):
            page_name = page_name[1:]

        if group_page:
            res = self.vkapi.groups.getById(group_ids=page_name)
            key = 'gid'
            # Group id must starts with - symbol
            k = -1
        else:
            res = self.vkapi.users.get(user_ids=page_name)
            key = 'uid'
            k = 1

        if not res:
            return

        return int(res[0][key])*k
