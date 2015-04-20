import re
import os
import json

from auth.providers import AuthBase
from auth.paths import AUTH_CFG_PATH


ADMIN_CONFIG_PATH = AUTH_CFG_PATH.joinpath("admins.json")


class SourcePerms(AuthBase):
    def __init__(self):
        self.permissions = {}

    def load(self):
        self.permissions.clear()
        if not os.path.exists(ADMIN_CONFIG_PATH):
            open(ADMIN_CONFIG_PATH, "w").close()
        else:
            with open(ADMIN_CONFIG_PATH) as file:
                admins = json.load(file)
                for uniqueid, permissions in admins.items():
                    self.permissions[uniqueid] = []
                    for permission in permissions:
                        self.permissions[uniqueid].append(re.compile(permission.replace(".", "\\.").replace("*", "(.*)")))

    def unload(self):
        self.permissions.clear()

    def is_player_authorized(self, uniqueid, level, permission, flag):
        if uniqueid in self.permissions:
            for re_permission in self.permissions[uniqueid]:
                if re_permission.match(permission) is not None:
                    return True
        return False

source_perms = SourcePerms()