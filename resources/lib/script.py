# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import sys
import xbmc
import xbmcgui
import resources.lib.utils as utils
import resources.lib.basedir as basedir
from resources.lib.fanarttv import FanartTV
from resources.lib.tmdb import TMDb
from resources.lib.traktapi import TraktAPI
from resources.lib.plugin import ADDON


class Script(object):
    def get_params(self):
        params = {}
        for arg in sys.argv:
            if arg == 'script.py':
                pass
            elif '=' in arg:
                arg_split = arg.split('=', 1)
                if arg_split[0] and arg_split[1]:
                    key, value = arg_split
                    value = value.strip('\'').strip('\"')
                    params.setdefault(key, value)
            else:
                params.setdefault(arg, True)
        return params

    def _sync_item_methods(self):
        return [
            {
                'method': 'history',
                'sync_type': 'watched',
                'allow_episodes': True,
                'name_add': xbmc.getLocalizedString(16103),
                'name_remove': xbmc.getLocalizedString(16104)},
            {
                'method': 'collection',
                'sync_type': 'collection',
                'allow_episodes': True,
                'name_add': ADDON.getLocalizedString(32289),
                'name_remove': ADDON.getLocalizedString(32290)},
            {
                'method': 'watchlist',
                'sync_type': 'watchlist',
                'name_add': ADDON.getLocalizedString(32291),
                'name_remove': ADDON.getLocalizedString(32292)},
            {
                'method': 'recommendations',
                'sync_type': 'recommendations',
                'name_add': ADDON.getLocalizedString(32293),
                'name_remove': ADDON.getLocalizedString(32294)}]

    def _sync_item_check(
            self, trakt_type, unique_id, season=None, episode=None, id_type=None,
            sync_type=None, method=None, name_add=None, name_remove=None, allow_episodes=False):
        if season is not None and (not allow_episodes or not episode):
            return
        if TraktAPI().is_sync(trakt_type, unique_id, season, episode, id_type, sync_type):
            return {'name': name_remove, 'method': '{}/remove'.format(method)}
        return {'name': name_add, 'method': method}

    def sync_item(self, trakt_type=None, unique_id=None, season=None, episode=None, id_type=None, **kwargs):
        with utils.busy_dialog():
            choices = [
                j for j in (
                    self._sync_item_check(trakt_type, unique_id, season, episode, id_type, **i)
                    for i in self._sync_item_methods()) if j]
        choice = xbmcgui.Dialog().contextmenu([i.get('name') for i in choices])
        if choice == -1:
            return
        with utils.busy_dialog():
            item_sync = TraktAPI().sync_item(
                choices[choice].get('method'), trakt_type, unique_id, id_type,
                season=season, episode=episode)
        if item_sync and item_sync.status_code in [200, 201, 204]:
            xbmcgui.Dialog().ok(ADDON.getLocalizedString(32295), ADDON.getLocalizedString(32297).format(
                choices[choice].get('name'), trakt_type, id_type.upper(), unique_id))
            xbmc.executebuiltin('Container.Refresh')
            return
        xbmcgui.Dialog().ok(ADDON.getLocalizedString(32295), ADDON.getLocalizedString(32296).format(
            choices[choice].get('name'), trakt_type, id_type.upper(), unique_id))

    def manage_artwork(self, ftv_id=None, ftv_type=None, **kwargs):
        if not ftv_id or not ftv_type:
            return
        choice = xbmcgui.Dialog().contextmenu([
            ADDON.getLocalizedString(32220),
            ADDON.getLocalizedString(32221)])
        if choice == -1:
            return
        if choice == 0:
            return FanartTV().select_artwork(ftv_id=ftv_id, ftv_type=ftv_type)
        if choice == 1:
            return FanartTV().refresh_all_artwork(ftv_id=ftv_id, ftv_type=ftv_type)

    def related_lists(self, tmdb_id=None, tmdb_type=None, season=None, episode=None, container_update=True, **kwargs):
        if not tmdb_id or not tmdb_type:
            return
        items = basedir.get_basedir_details(tmdb_type=tmdb_type, tmdb_id=tmdb_id, season=season, episode=episode)
        if not items or len(items) <= 1:
            return
        choice = xbmcgui.Dialog().contextmenu([i.get('label') for i in items])
        if choice == -1:
            return
        item = items[choice]
        params = item.get('params')
        if not params:
            return
        item['params']['tmdb_id'] = tmdb_id
        item['params']['tmdb_type'] = tmdb_type
        if season is not None:
            item['params']['season'] = season
            if episode is not None:
                item['params']['episode'] = episode
        if not container_update:
            return item
        path = 'Container.Update({})' if xbmc.getCondVisibility("Window.IsMedia") else 'ActivateWindow(videos,{},return)'
        path = path.format(utils.get_url(path=item.get('path'), **item.get('params')))
        xbmc.executebuiltin(path)

    def refresh_details(self, tmdb_id=None, tmdb_type=None, season=None, episode=None, **kwargs):
        if not tmdb_id or not tmdb_type:
            return
        with utils.busy_dialog():
            details = TMDb().get_details(tmdb_type, tmdb_id, season=season, episode=episode)
        if details:
            xbmcgui.Dialog().ok('TMDbHelper', ADDON.getLocalizedString(32234).format(tmdb_type, tmdb_id))
            xbmc.executebuiltin('Container.Refresh')

    def router(self):
        self.params = self.get_params()
        if not self.params:
            return
        if self.params.get('sync_item'):
            return self.sync_item(**self.params)
        if self.params.get('manage_artwork'):
            return self.manage_artwork(**self.params)
        if self.params.get('refresh_details'):
            return self.refresh_details(**self.params)
        if self.params.get('related_lists'):
            return self.related_lists(**self.params)
