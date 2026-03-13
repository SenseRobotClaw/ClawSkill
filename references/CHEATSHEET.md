# 元萝卜下棋机器人 速查表

## 连接

```
SSH: ssh root@192.168.199.10
API: http://192.168.199.10:60010
```

## HTTP API 速查

| 操作 | URL |
|------|-----|
| 看棋盘 | `curl 'http://192.168.199.10:60010/skill-look-board'` |
| 复位机械臂 | `curl 'http://192.168.199.10:60010/skill-move-home'` |
| 取落子 | `curl 'http://192.168.199.10:60010/skill-move-tcp?x=X&y=Y&action=N'` |
| 自由取子 | `curl 'http://192.168.199.10:60010/skill-catch-box'` |
| 清理棋盘 | `curl 'http://192.168.199.10:60010/skill-clean-board'` |
| 语音播报 | `curl 'http://192.168.199.10:60010/skill-tts-chinese?content=TEXT'` |

action: 0=移动 1=取子 2=落子

## SSH 指令速查

| 操作 | 命令 |
|------|------|
| 恢复下棋 | `/etc/init.d/bi-app-sensechess restart` |
| 停止下棋 | `kkill proce sense` |
| 停止监控 | `kkill proce monitor` |
| 机械臂控制 | `robotMcu -- 0x11 0x12 x y 255 n 0 0` |
| 表情控制 | `media_service start_play_animation NUM` |

## 表情编号

002=快乐 003=哭 004=默认 008=兴趣 011=摇头轻快 012=摇头否认 013=消失 014=出现

## 坐标

- 棋盘: (0,0)右上 → (12,12)左下
- 右棋盒: (-3.8,0) → (-1.8,7)
- 左棋盒: (14.2,0) → (15.8,7)

## 标准操作流程

```bash
# 1. 先看棋盘
curl 'http://192.168.199.10:60010/skill-look-board'
# 2. 取子
curl 'http://192.168.199.10:60010/skill-catch-box'
# 3. 落子到 (6,6)
curl 'http://192.168.199.10:60010/skill-move-tcp?x=6&y=6&action=2'
```
