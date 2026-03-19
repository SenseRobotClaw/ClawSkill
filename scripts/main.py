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
            url += "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
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

    def detect_box(self):
        """查找棋盒棋子的位置
        returns: list of pieces, e.g. [{"color":1,"x":-3.1,"y":1.5}] (color 1=黑, 2=白)
        """
        data = self._api_get("/skill-detect-box")
        try:
            res = json.loads(data)
            if res.get("ok") and res.get("result") == "success":
                return res.get("pieces", [])
        except json.JSONDecodeError:
            pass
        return []

    def detect_board(self):
        """查找棋盘棋子的位置
        returns: list of pieces, e.g. [{"color":1,"x":3,"y":4}] (color 1=黑, 2=白)
        """
        data = self._api_get("/skill-detect-board")
        try:
            res = json.loads(data)
            if res.get("ok") and res.get("result") == "success":
                return res.get("pieces", [])
        except json.JSONDecodeError:
            pass
        return []

    def clean_board(self):
        """清理棋盘 (异步调用，返回任务状态)
        返回包含 result (running/done/error) 和 detail 的 JSON 对象
        """
        data = self._api_get("/skill-clean-board")
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return {"result": "error", "detail": "Invalid JSON response"}

    def tts(self, content):
        """语音播报"""
        return self._api_get("/skill-tts-chinese", {"content": content})

    def show_emotion(self, code):
        """显示表情"""
        return self._api_get("/skill-show-emotion", {"code": code})

    def show_image(self, image_path):
        """显示图片"""
        # Using curl for multipart/form-data upload as it's simpler and more robust
        # than manual multipart construction in standard library without requests
        url = f"{self.api_base}/skill-show-image"
        print(f"📡 POST {url} image={image_path}")
        
        try:
            # Use curl to upload the file
            cmd = ['curl', '--location', url, '--form', f'image=@"{image_path}"']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ 响应: {result.stdout[:500]}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"❌ Curl failed: {e.stderr}")
            return ""

    def take_photo(self, camera_id):
        """拍照 (0=前置 1=右边 2=左边)"""
        return self._api_get("/skill-take-photo", {"id": camera_id}, binary=True)

    def record(self, code):
        """录音 (0=开始 1=结束)"""
        return self._api_get("/skill-record", {"code": code}, binary=(code == 1))


    # ── 复合操作 ──

    def pick_with_retry(self):
        """从棋盒智能取子（CV检测 + 缓存重试）"""
        pieces = self.detect_box()
        if not pieces:
            print("⚠️ 未检测到棋子")
            pieces = []

        cached_pieces = list(pieces)
        while cached_pieces:
            piece = cached_pieces.pop(0)  # 无论成功失败，都从缓存中移除该位置
            base_x = piece.get("x", 0)
            base_y = piece.get("y", 0)

            x = round(base_x, 3)
            y = round(base_y, 3)

            result = self.move_tcp(x, y, 1)
            try:
                res_json = json.loads(result)
                is_success = res_json.get("ok") and res_json.get("result") == "success"
            except json.JSONDecodeError:
                is_success = "0" in result or "ret:0" in result

            if is_success:
                print("✅ 取子成功")
                return True
            print("⚠️ 取子失败，使用缓存的下个位置重试...")

        print("❌ 取子失败，请整理棋盒或放入新棋子")
        self.tts("取子失败，请整理棋盒或放入新棋子")
        return False

    def place_stone(self, x, y):
        """完整落子流程：移动 → 落子"""
        print(f"🎯 落子到 ({x}, {y})")
        result = self.move_tcp(x, y, 2)
        try:
            res_json = json.loads(result)
            is_success = res_json.get("ok") and res_json.get("result") == "success"
        except json.JSONDecodeError:
            is_success = "0" in result or "ret:0" in result

        if is_success:
            print("✅ 落子完成")
            return True
        print(f"❌ 落子失败: {result.strip()}")
        return False


# ── CLI ──

def cmd_look(args):
    RobotClient().look_board()

def cmd_place(args):
    RobotClient().place_stone(args.x, args.y)

def cmd_clean(args):
    import time
    print("开始清理棋盘任务...")
    while True:
        res = RobotClient().clean_board()
        status = res.get("result", "error")
        detail = res.get("detail", "")
        
        if status == "running":
            print(f"⏳ {detail} (等待 10 秒后查询...)")
            time.sleep(10)
        elif status == "done":
            print(f"✅ 清理完成: {detail}")
            break
        else:
            print(f"❌ 清理异常: {detail}")
            break

def cmd_home(args):
    RobotClient().move_home()

def cmd_tts(args):
    RobotClient().tts(args.content)

def cmd_pick(args):
    RobotClient().pick_with_retry()

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


def cmd_detect(args):
    client = RobotClient()
    if args.board:
        print(json.dumps(client.detect_board(), indent=2))
    else:
        print(json.dumps(client.detect_box(), indent=2))

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

    sub.add_parser("pick", help="从棋盒取子(智能取子)")

    p = sub.add_parser("photo", help="拍照")
    p.add_argument("id", type=int, choices=[0, 1, 2], help="摄像头ID (0=前置 1=右 2=左)")

    p = sub.add_parser("record", help="录音")
    p.add_argument("action", choices=["start", "stop"], help="start=开始 stop=结束并保存")

    p = sub.add_parser("detect", help="查找棋盒棋子")
    p.add_argument("--board", action="store_true", help="查找棋盘上的棋子而不是棋盒")
    
    p = sub.add_parser("show_image", help="显示图片")
    p.add_argument("path", help="图片路径 (仅支持PNG)")

    args = parser.parse_args()
    cmds = {
        "look": cmd_look, "place": cmd_place, "clean": cmd_clean,
        "home": cmd_home, "tts": cmd_tts, 
        "pick": cmd_pick,
        "expression": cmd_expression, "photo": cmd_photo, "record": cmd_record,
        "detect": cmd_detect,
        "show_image": lambda a: RobotClient().show_image(a.path)
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
