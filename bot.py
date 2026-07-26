#!/usr/bin/env python3
# bot.py
"""
阿尔比恩装备推荐机器人 - KOOK版 (面向对象模块化)
入口文件，启动机器人并处理消息事件。
"""

import os
import asyncio
from dotenv import load_dotenv
from khl import Bot, Message
from manager import BuildManager
from threading import Thread
from ai_client import get_qwen_response

# 加载环境变量
load_dotenv()
TOKEN = os.getenv('KOOK_BOT_TOKEN')
if not TOKEN:
    raise ValueError("请在.env文件中设置KOOK_BOT_TOKEN")

bot = Bot(token=TOKEN)
manager = BuildManager()

# ========== 辅助函数 ==========
def get_help_text() -> str:
    return """**🛡️ 阿尔比恩装备推荐机器人 (面向对象模块化)**  
`!albion <武器名>` - **同时展示PVE和PVP配装** (例: `!albion 单手斧`)  
`!albion pve <武器名>` - 仅查看PVE配装  
`!albion pvp <武器名>` - 仅查看PVP配装  
`!albion pve list` - 列出所有PVE武器  
`!albion pvp list` - 列出所有PVP武器  
`!albion random` - 随机推荐一套配装  
`!albion help` - 显示本帮助

📌 **提示**：武器名支持中英文别名，不区分大小写。装备描述自动从括号中提取。"""

def build_list_message(module: str) -> str:
    names = manager.get_weapon_list(module)
    if not names:
        return f"📜 当前 {module.upper()} 模块暂无武器数据。"
    return f"📜 {module.upper()} 支持的武器:\n" + "、".join(names)

# ========== 消息事件 ==========
@bot.on_message()
async def on_message(msg: Message):
    if msg.author.bot:
        return

    content = msg.content.strip()
    if not (content.startswith("!albion") or content.startswith("!ai")):
        return

    parts = content.split()
    if len(parts) < 2:
        # 如果只输入了 !albion 或 !ai，展示帮助
        if content.startswith("!ai"):
            await msg.reply("请提出你的问题，例如：`!ai 阿尔比恩单手斧如何配装？`")
        else:
            await msg.reply(get_help_text())
        return

    # 根据命令前缀分支处理
    cmd = parts[0].lower()  # 获取实际命令前缀

    # ===== 处理 !ai 命令 =====
    if cmd == "!ai":
        question = " ".join(parts[1:])
        if not question:
            await msg.reply("请提出你的问题，例如：`!ai 阿尔比恩单手斧如何配装？`")
            return
        await msg.reply("🤔 正在思考，请稍候...")
        reply = get_qwen_response(question)
        await msg.reply(reply)
        return

    # ===== 处理 !albion 命令 =====
    if cmd == "!albion":
        sub_cmd = parts[1].lower() if len(parts) > 1 else ""

        if sub_cmd == "help":
            await msg.reply(get_help_text())
            return

        if sub_cmd == "random":
            await msg.reply(manager.random_build())
            return

        if sub_cmd == "list":
            await msg.reply("请指定模块：`!albion pve list` 或 `!albion pvp list`")
            return

        # 处理 pve / pvp
        if sub_cmd in ("pve", "pvp"):
            if len(parts) < 3:
                await msg.reply(f"请指定武器名称，例如 `!albion {sub_cmd} 单手斧`")
                return
            second = parts[2].lower()
            if second == "list":
                await msg.reply(build_list_message(sub_cmd))
                return
            weapon_input = " ".join(parts[2:])
            key, build = manager.match_weapon(weapon_input, sub_cmd)
            if key and build:
                image_url = manager.get_image_url(key, sub_cmd)
                await msg.reply(build.to_message(key, sub_cmd, image_url))
            else:
                await msg.reply(f"❌ 在 {sub_cmd.upper()} 模块中未找到「{weapon_input}」。")
            return

        # 无子命令，同时展示 PVE 和 PVP
        weapon_input = " ".join(parts[1:])
        matches = manager.match_any(weapon_input)
        if not matches:
            await msg.reply(f"❌ 未找到「{weapon_input}」的配装信息（PVE和PVP均无）。\n请使用 `!albion pve list` 或 `!albion pvp list` 查看可用武器。")
            return

        for key, build, module in matches:
            image_url = manager.get_image_url(key, module)
            await msg.reply(build.to_message(key, module, image_url))
        return

# ========== 启动 ==========
if __name__ == "__main__":
    # === 修复事件循环缺失问题 ===
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())


    def start_web_server():
        """启动一个极简的 Web 服务器，用于通过 Render 的端口检测"""
        from http.server import HTTPServer, BaseHTTPRequestHandler

        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")

        port = int(os.environ.get("PORT", 10000))
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        print(f"✅ 健康检查 Web 服务器已启动，监听端口 {port}")
        server.serve_forever()


    # 在后台线程中启动 Web 服务器
    Thread(target=start_web_server, daemon=True).start()

    print("🤖 阿尔比恩装备推荐机器人 (模块化) 启动中...")
    print("装备描述自动从括号中提取，缺失装备显示'无'。")
    try:
        bot.run()
    except KeyboardInterrupt:
        print("机器人已关闭")
    except Exception as e:
        print(f"运行时错误: {e}")