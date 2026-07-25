# manager.py
"""BuildManager：管理配装数据、匹配、列表、随机"""

import random
from models import Build
from data import PVE_BUILDS_RAW, PVP_BUILDS_RAW, WEAPON_IMAGE_MAP


class BuildManager:
    def __init__(self):
        self.pve_builds = {}
        self.pvp_builds = {}
        self.alias_map = {}          # 别名 -> (武器键, 模块)
        self._load_builds()

    def _load_builds(self):
        # 加载PVE
        for key, data in PVE_BUILDS_RAW.items():
            build = Build(data['equipment'], data['scene'], data.get('skills', ''), data.get('description', ''))
            self.pve_builds[key] = build
            self._register_aliases(key, data.get('aliases', []), 'pve')

        # 加载PVP
        for key, data in PVP_BUILDS_RAW.items():
            build = Build(data['equipment'], data['scene'], data.get('skills', ''), data.get('description', ''))
            self.pvp_builds[key] = build
            self._register_aliases(key, data.get('aliases', []), 'pvp')

    def _register_aliases(self, key: str, aliases: list, module: str):
        self.alias_map[key.lower()] = (key, module)
        for alias in aliases:
            self.alias_map[alias.lower()] = (key, module)

    def get_build(self, weapon_key: str, module: str):
        builds = self.pve_builds if module == 'pve' else self.pvp_builds
        return builds.get(weapon_key)

    def match_weapon(self, name: str, module: str):
        """在指定模块中匹配，返回(武器键, Build对象)或(None, None)"""
        name_lower = name.lower().strip()
        builds = self.pve_builds if module == 'pve' else self.pvp_builds
        # 1. 精确匹配键
        for key in builds:
            if key.lower() == name_lower:
                return key, builds[key]
        # 2. 别名匹配
        if name_lower in self.alias_map:
            alias_key, alias_module = self.alias_map[name_lower]
            if alias_module == module:
                return alias_key, builds.get(alias_key)
        return None, None

    def match_any(self, name: str):
        """在所有模块中匹配，返回列表 [(武器键, Build对象, 模块), ...]"""
        results = []
        pve_key, pve_build = self.match_weapon(name, 'pve')
        if pve_key:
            results.append((pve_key, pve_build, 'pve'))
        pvp_key, pvp_build = self.match_weapon(name, 'pvp')
        if pvp_key and pvp_key != pve_key:
            results.append((pvp_key, pvp_build, 'pvp'))
        return results

    def get_weapon_list(self, module: str):
        builds = self.pve_builds if module == 'pve' else self.pvp_builds
        return list(builds.keys())

    def random_build(self) -> str:
        """随机返回一个配装消息字符串"""
        if self.pve_builds:
            key = random.choice(list(self.pve_builds.keys()))
            build = self.pve_builds[key]
            return build.to_message(key, 'pve', self.get_image_url(key, 'pve'))
        elif self.pvp_builds:
            key = random.choice(list(self.pvp_builds.keys()))
            build = self.pvp_builds[key]
            return build.to_message(key, 'pvp', self.get_image_url(key, 'pvp'))
        else:
            return "暂无配装数据。"

    def get_image_url(self, weapon_key: str, module: str) -> str:
        return None