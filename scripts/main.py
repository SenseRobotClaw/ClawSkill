#!/usr/bin/env python3
"""元萝卜下棋机器人控制客户端"""

import argparse
import json
import random
import subprocess
import sys
import urllib.request
import urllib.parse

ROBOT_IP = "192.168.199.10"
API_BASE = f"http://{ROBOT_IP}:60010"


class RobotClient:
    """元萝卜机器人控制客户端"""

    def __init__(self, ip=ROBOT_IP):
        self.ip = ip
        self.api_base = f"http://{ip}:60010"
        
    # ── HTTP API ──

    def _api_get(self, path, params=None):
        url = f"{self.api_base}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        print(f"📡 GET {url}")
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            print(f"✅ 响应: {body[:500]}")
            return body

    def look_board(self):
        """查看当前棋盘状态"""
        return self._api_get("/skill-look-board")

    def move_home(self):
        """复位机械臂"""
        return self._api_get("/skill-move-home")

    def move_tcp(self, x, y, action):
        """取落子控制 (action: 0=移动 1=取子 2=落子)"""
        return self._api_get("/skill-move-tcp", {"x": x, "y": y, "action": action})

    def catch_box(self):
        """自由取子（CV能力）"""
        return self._api_get("/skill-catch-box")

    def clean_board(self):
        """清理棋盘"""
        return self._api_get("/skill-clean-board")

    def tts(self, content):
        """语音播报"""
        return self._api_get("/skill-tts-chinese", {"content": content})


    # ── 复合操作 ──

    def pick_with_retry(self, box="right", max_retries=3):
        """从棋盒取子，失败自动重试（偏移0.5步长）"""
        if box == "right":
            base_x, base_y = random.uniform(-3.8, -1.8), random.uniform(0, 7)
        else:
            base_x, base_y = random.uniform(14.2, 15.8), random.uniform(0, 7)

        for attempt in range(max_retries + 1):
            x = base_x + random.uniform(-0.5, 0.5) * (1 if attempt > 0 else 0)
            y = base_y + random.uniform(-0.5, 0.5) * (1 if attempt > 0 else 0)
            result = self.robot_mcu(round(x, 1), round(y, 1), 1)
            if result.strip() == "0":
                print(f"✅ 取子成功 (第{attempt + 1}次)")
                return True
            print(f"⚠️ 取子失败 (第{attempt + 1}次)，重试中...")
        print("❌ 取子失败，已达最大重试次数")
        return False

    def place_stone(self, x, y):
        """完整落子流程：看棋盘 → 取子 → 移动 → 落子"""
        print(f"🎯 落子到 ({x}, {y})")
        self.look_board()
        self.catch_box()
        self.move_tcp(x, y, 2)
        print("✅ 落子完成")


# ── CLI ──

def cmd_look(args):
    RobotClient().look_board()

def cmd_place(args):
    RobotClient().place_stone(args.x, args.y)

def cmd_clean(args):
    RobotClient().clean_board()

def cmd_home(args):
    RobotClient().move_home()

def cmd_tts(args):
    RobotClient().tts(args.content)

def cmd_pick(args):
    RobotClient().pick_with_retry(box=args.box)


def main():
    parser = argparse.ArgumentParser(description="元萝卜下棋机器人控制")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("look", help="查看棋盘状态")
    sub.add_parser("clean", help="清理棋盘")
    sub.add_parser("home", help="复位机械臂")

    p = sub.add_parser("place", help="落子")
    p.add_argument("x", type=float, help="横坐标")
    p.add_argument("y", type=float, help="纵坐标")

    p = sub.add_parser("tts", help="语音播报")
    p.add_argument("content", help="播报内容")

    p = sub.add_parser("expression", help="表情控制")
    p.add_argument("number", help="表情编号 (002=快乐 003=哭 004=默认 008=兴趣)")

    p = sub.add_parser("pick", help="从棋盒取子")
    p.add_argument("--box", choices=["left", "right"], default="right", help="棋盒选择")

    args = parser.parse_args()
    cmds = {
        "look": cmd_look, "place": cmd_place, "clean": cmd_clean,
        "home": cmd_home, "tts": cmd_tts, 
        "pick": cmd_pick, 
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
