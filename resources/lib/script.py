# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import sys
import xbmc
import xbmcgui
import resources.lib.utils as utils
from resources.lib.fanarttv import FanartTV
from resources.lib.tmdb import TMDb
from resources.lib.plugin import ADDON


class Script(object):
    def __init__(self):
        self.params = self.get_params()

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

    def refresh_details(self, tmdb_id=None, tmdb_type=None, season=None, episode=None, **kwargs):
        if not tmdb_id or not tmdb_type:
            return
        with utils.busy_dialog():
            details = TMDb().get_details(tmdb_type, tmdb_id, season=season, episode=episode)
        if details:
            xbmcgui.Dialog().ok('TMDbHelper', ADDON.getLocalizedString(32234).format(tmdb_type, tmdb_id))
            xbmc.executebuiltin('Container.Refresh')

    def router(self):
        if not self.params:
            return
        if self.params.get('manage_artwork'):
            return self.manage_artwork(**self.params)
        if self.params.get('refresh_details'):
            return self.refresh_details(**self.params)
