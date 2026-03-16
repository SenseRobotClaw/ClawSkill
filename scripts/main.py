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

    def _api_get(self, path, params=None, binary=False):
        url = f"{self.api_base}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        print(f"📡 GET {url}")
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            if binary:
                print(f"✅ 响应: [Binary Data] {len(data)} bytes")
                return data
            body = data.decode("utf-8")
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

    def catch_box(self, color=0):
        """自由取子（CV能力）
        color: 0=任意, 1=黑子, 2=白子
        """
        return self._api_get("/skill-catch-box", {"color": color})

    def clean_board(self):
        """清理棋盘"""
        return self._api_get("/skill-clean-board")

    def tts(self, content):
        """语音播报"""
        return self._api_get("/skill-tts-chinese", {"content": content})

    def show_emotion(self, code):
        """显示表情"""
        return self._api_get("/skill-show-emotion", {"code": code})

    def take_photo(self, camera_id):
        """拍照 (0=前置 1=右边 2=左边)"""
        return self._api_get("/skill-take-photo", {"id": camera_id}, binary=True)

    def record(self, code):
        """录音 (0=开始 1=结束)"""
        return self._api_get("/skill-record", {"code": code}, binary=(code == 1))


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
            result = self.move_tcp(round(x, 1), round(y, 1), 1)
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

def cmd_catch(args):
    RobotClient().catch_box(color=args.color)

def cmd_expression(args):
    RobotClient().show_emotion(args.code)

def cmd_photo(args):
    data = RobotClient().take_photo(args.id)
    filename = f"photo_{args.id}.jpg"
    with open(filename, "wb") as f:
        f.write(data)
    print(f"✅ 照片已保存: {filename}")

def cmd_record(args):
    if args.action == "start":
        RobotClient().record(0)
    elif args.action == "stop":
        data = RobotClient().record(1)
        filename = "record.pcm"
        with open(filename, "wb") as f:
            f.write(data)
        print(f"✅ 录音已保存: {filename}")


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
    p.add_argument("code", help="表情编号 (002=快乐 003=哭 004=默认 008=兴趣)")

    p = sub.add_parser("pick", help="从棋盒取子(盲取)")
    p.add_argument("--box", choices=["left", "right"], default="right", help="棋盒选择")

    p = sub.add_parser("catch", help="从棋盒取子(CV)")
    p.add_argument("--color", type=int, choices=[0, 1, 2], default=0, help="0=任意 1=黑 2=白")

    p = sub.add_parser("photo", help="拍照")
    p.add_argument("id", type=int, choices=[0, 1, 2], help="摄像头ID (0=前置 1=右 2=左)")

    p = sub.add_parser("record", help="录音")
    p.add_argument("action", choices=["start", "stop"], help="start=开始 stop=结束并保存")

    args = parser.parse_args()
    cmds = {
        "look": cmd_look, "place": cmd_place, "clean": cmd_clean,
        "home": cmd_home, "tts": cmd_tts, 
        "pick": cmd_pick, "catch": cmd_catch,
        "expression": cmd_expression, "photo": cmd_photo, "record": cmd_record
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
