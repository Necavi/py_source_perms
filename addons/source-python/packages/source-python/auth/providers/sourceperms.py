import re
import os
import json

try:
    import sqlalchemy
except ImportError:
    pass

from configobj import ConfigObj

from auth.providers import AuthBase
from auth.paths import AUTH_CFG_PATH


PLUGIN_CONFIG_PATH = AUTH_CFG_PATH.joinpath("sourceperms.ini")


class PermissionBase(set):
    def __init__(self, name):
        super().__init__()
        self.parents = set()
        self.cache = set()
        self.name = name
        self.data = {}

    def __hash__(self):
        return hash(self.name)

    def add(self, *args, **kwargs):
        super().add(*args, **kwargs)
        self.refresh_cache()

    def remove(self, *args, **kwargs):
        super().remove(*args, **kwargs)
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

    def get_data(self, node):
        if node in self.data:
            return self.data[node]
        else:
            for parent in self.parents:
                data = parent.get_data(node)
                if data is not None:
                    return data

    def add_parent(self, parent):
        self.parents.add(groups[parent])
        groups[parent].children.add(self)


class PermissionPlayer(PermissionBase):
    def __new__(cls, name):
        if name in players:
            return players[name]
        else:
            player = super().__new__(cls)
            players[name] = player
            return player


class PermissionGroup(PermissionBase):
    def __new__(cls, name):
        if name in groups:
            return groups[name]
        else:
            group = super().__new__(cls)
            groups[name] = group
            return group

    def __init__(self, name):
        super().__init__(name)
        self.children = set()


class PermissionoSource(object):
    name = ""
    options = {}

    def load(self):
        pass

    def unload(self):
        pass


class SimplePermissionSource(PermissionoSource):
    name = "simple"
    options = {
        "config_path": AUTH_CFG_PATH.joinpath("simple.txt")
    }

    def load(self):
        if os.path.exists(self.options["config_path"]):
            with open(self.options["config_path"]) as file:
                for uniqueid in file.readlines():
                    players[uniqueid].add("*")


class FlatfilePermissionSource(PermissionoSource):
    name = "flatfile"
    options = {
        "admin_config_path": AUTH_CFG_PATH.joinpath("admins.json"),
        "group_config_path": AUTH_CFG_PATH.joinpath("groups.json")
    }

    def load(self):
        self.load_config(players, self.options["admin_config_path"])
        self.load_config(groups, self.options["group_config_path"])

    def load_config(self, store, path):
        if os.path.exists(path):
            with open(path) as file:
                nodes = json.load(file)
                for nodename, node in nodes.items():
                    for permission in node.get("permissions", set()):
                        if permission != "":
                            store[nodename].add(permission)
                    for group in node.get("parents", set()):
                        store[nodename].add_parent(group)


class SourcePerms(AuthBase):
    def load(self):
        players.clear()
        groups.clear()
        for source in active_permission_sources:
            source.load()

    def unload(self):
        players.clear()
        groups.clear()

    def is_player_authorized(self, uniqueid, level, permission, flag):
        if uniqueid not in players:
            return groups["default"].has_permission(permission)
        return players[uniqueid].has_permission(permission)


class PermissionDict(dict):
    def __init__(self, permission_type):
        super().__init__()
        self.permission_type = permission_type

    def __missing__(self, key):
        self[key] = self.permission_type(key)
        return self[key]


groups = PermissionDict(PermissionGroup)
players = PermissionDict(PermissionPlayer)


permission_sources = {
    FlatfilePermissionSource.name: FlatfilePermissionSource,
    SimplePermissionSource.name: SimplePermissionSource
}

active_permission_sources = []


def load_permission_source(source):
    if source in permission_sources:
        active_permission_sources.append(permission_sources[source]())

config = ConfigObj()
config["Config"] = {
    "PermissionSource": "flatfile"
}
backends = {}
for source in permission_sources.values():
    backends[source.name] = source.options
config["backends"] = backends
config.filename = PLUGIN_CONFIG_PATH
if os.path.exists(PLUGIN_CONFIG_PATH):
    user_config = ConfigObj(PLUGIN_CONFIG_PATH)
    config.merge(user_config)
config.write()
for source in permission_sources.values():
    source.options = config["backends"][source.name]
permission_source = config["Config"]["PermissionSource"]
if isinstance(permission_source, list):
    for permission_source in config["Config"]["PermissionSource"]:
        load_permission_source(permission_source)
else:
    load_permission_source(config["Config"]["PermissionSource"])

source_perms = SourcePerms()