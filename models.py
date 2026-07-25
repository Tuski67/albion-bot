# models.py
"""数据模型：Equipment 和 Build，支持从装备标签库构建"""

from data import EQUIPMENT_DB

class Equipment:
    """装备项，可从装备ID构建，也兼容旧字符串格式"""
    def __init__(self, raw_or_id):
        """
        参数可以是：
        1. 字符串ID（在 EQUIPMENT_DB 中）
        2. 已包含描述的字符串 "名称 (描述)"（兼容旧格式）
        """
        self.is_valid = False
        self.name = ""
        self.description = ""

        if not raw_or_id:
            return

        # 先尝试作为ID查找
        if raw_or_id in EQUIPMENT_DB:
            info = EQUIPMENT_DB[raw_or_id]
            self.name = info["name"]
            self.description = info.get("desc", "")
            self.is_valid = True
            return

        # 若不是ID，则可能是旧格式 "名称 (描述)" 或纯名称
        raw_str = raw_or_id
        if "(" in raw_str and ")" in raw_str:
            name_part, desc_part = raw_str.split("(", 1)
            self.name = name_part.strip()
            self.description = desc_part.rstrip(")").strip()
        else:
            self.name = raw_str.strip()
            self.description = ""
        self.is_valid = True

    def display(self) -> str:
        if not self.is_valid:
            return "无"
        if self.description:
            return f"{self.name} ({self.description})"
        return self.name


class Build:
    """配装对象，equipment 字段为装备ID或旧格式字符串"""
    def __init__(self, equipment_data: dict, scene: str, skills: str = "", description: str = ""):
        self.weapon = Equipment(equipment_data.get('weapon', ''))
        self.offhand = Equipment(equipment_data.get('offhand', '')) if equipment_data.get('offhand') else None
        self.helmet = Equipment(equipment_data.get('helmet', '')) if equipment_data.get('helmet') else None
        self.chest = Equipment(equipment_data.get('chest', '')) if equipment_data.get('chest') else None
        self.boots = Equipment(equipment_data.get('boots', '')) if equipment_data.get('boots') else None
        self.cape = Equipment(equipment_data.get('cape', '')) if equipment_data.get('cape') else None
        self.food = Equipment(equipment_data.get('food', '')) if equipment_data.get('food') else None
        self.potion = Equipment(equipment_data.get('potion', '')) if equipment_data.get('potion') else None
        self.scene = scene
        self.skills = skills
        self.description = description

    def to_message(self, weapon_key: str, module: str, image_url: str = None) -> str:
        """生成完整配装消息"""
        msg = ""
        if image_url:
            msg += f"![{weapon_key} {module.upper()}配装图]({image_url})\n\n"

        msg += f"**⚔️ {weapon_key} - {module.upper()} 配装**\n"
        msg += f"🎯 场景：{self.scene}\n\n"
        msg += f"🔹 武器：{self.weapon.display()}\n"
        if self.offhand:
            msg += f"🔸 副手：{self.offhand.display()}\n"
        msg += f"🪖 头盔：{self.helmet.display() if self.helmet else '无'}\n"
        msg += f"🛡️ 胸甲：{self.chest.display() if self.chest else '无'}\n"
        msg += f"👢 鞋子：{self.boots.display() if self.boots else '无'}\n"
        msg += f"🧥 披风：{self.cape.display() if self.cape else '普通披风'}\n"
        msg += f"🍗 食物：{self.food.display() if self.food else '炖牛肉'}\n"
        msg += f"🧪 药水：{self.potion.display() if self.potion else '治疗药水'}\n"
        if self.skills:
            msg += f"\n✨ 技能：{self.skills}\n"
        if self.description:
            msg += f"\n💬 说明：{self.description}\n"
        return msg