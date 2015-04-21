import re
import os
import json

from configobj import ConfigObj

from auth.providers import AuthBase
from auth.paths import AUTH_CFG_PATH


PLUGIN_CONFIG_PATH = AUTH_CFG_PATH.joinpath("sourceperms.ini")


class PermissionBase(set):
    def __init__(self, permissions=None, parents=None):
        super().__init__()
        if permissions is not None:
            [self.add(x) for x in permissions]
        self.parents = [] if parents is None else parents
        self.cache = set()

    def add(self, *args, **kwargs):
        super().add(*args, **kwargs)
        self.refresh_cache()

    @staticmethod
    def compile_permission(permission):
        return re.compile(permission.replace(".", "\\.").replace("*", "(.*)"))

    def refresh_cache(self):
        self.cache.clear()
        for permission in self:
            self.cache.add(self.compile_permission(permission))

    def has_permission(self, permission):
        for re_perm in self.cache:
            if re_perm.match(permission):
                return True
        for parent in self.parents:
            if parent.has_permission(permission):
                return True
        return False

    def list_permissions(self):
        perms = set()
        perms.update(self)
        for parent in self.parents:
            perms.update(parent.list_permissions())
        return perms


class PermissionGroup(PermissionBase):
    def __init__(self, permissions=None, parents=None, children=None):
        super().__init__(permissions, parents)
        self.children = [] if children is None else children


class FlatfilePermissionSource(AuthBase):
    ADMIN_CONFIG_PATH = AUTH_CFG_PATH.joinpath("admins.json")
    GROUP_CONFIG_PATH = AUTH_CFG_PATH.joinpath("groups.json")

    def __init__(self):
        self.groups = {}
        self.players = {}

    def load(self):
        self.load_groups()
        self.load_players()

    def load_players(self):
        self.players.clear()
        if os.path.exists(self.ADMIN_CONFIG_PATH):
            with open(self.ADMIN_CONFIG_PATH) as file:
                admins = json.load(file)
                for uniqueid, admin in admins.items():
                    if uniqueid not in self.players:
                        self.players[uniqueid] = PermissionBase()
                    for permission in admin.get("permissions", set()):
                        if permission != "":
                            self.players[uniqueid].add(permission)
                    for group in admin.get("groups", set()):
                        if group not in self.groups:
                            self.groups[group] = PermissionGroup()
                        self.players[uniqueid].parents.append(self.groups[group])
                        self.groups[group].children.append(self.players[uniqueid])

    def load_groups(self):
        self.groups.clear()
        if os.path.exists(self.GROUP_CONFIG_PATH):
            with open(self.GROUP_CONFIG_PATH) as file:
                groups = json.load(file)
                for groupname, group in groups.items():
                    if groupname not in self.groups:
                        self.groups[groupname] = PermissionGroup()
                    for permission in group.get("permissions", set()):
                        if permission != "":
                            self.groups[groupname].add(permission)
                    for parent in group.get("parents", set()):
                        if parent not in self.groups:
                            self.groups[parent] = PermissionGroup()
                        self.groups[groupname].parents.append(self.groups[parent])
                        self.groups[parent].children.append(self.groups[groupname])

    def unload(self):
        self.groups.clear()
        self.players.clear()

    def is_player_authorized(self, uniqueid, level, permission, flag):
        if uniqueid in self.players:
            return self.players[uniqueid].has_permission(permission)
        return False

permission_sources = {
    "flatfile": FlatfilePermissionSource
}

config = ConfigObj()
config["Config"] = {
    "PermissionSource": "flatfile"
}
config.filename = PLUGIN_CONFIG_PATH
if os.path.exists(PLUGIN_CONFIG_PATH):
    user_config = ConfigObj(PLUGIN_CONFIG_PATH)
    config.merge(user_config)
config.write()
permission_source = config["Config"]["PermissionSource"]
if permission_source in permission_sources:
    source_perms = permission_sources[permission_source]()
else:
    print("[SourcePerms] Permission source not found.")