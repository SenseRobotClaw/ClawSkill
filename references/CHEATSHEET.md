# 元萝卜下棋机器人 速查表

## 连接

```
API: http://192.168.199.10:60010
```

## HTTP API 速查

| 操作 | URL |
|------|-----|
| 看棋盘 | `curl 'http://192.168.199.10:60010/skill-look-board'` |
| 复位机械臂 | `curl 'http://192.168.199.10:60010/skill-move-home'` |
| 取落子 | `curl 'http://192.168.199.10:60010/skill-move-tcp?x=X&y=Y&action=N'` |
| 查找棋盒棋子 | `curl 'http://192.168.199.10:60010/skill-detect-box'` |
| 查找棋盘棋子 | `curl 'http://192.168.199.10:60010/skill-detect-board'` |
| 清理棋盘 | `curl 'http://192.168.199.10:60010/skill-clean-board'` (需轮询判断 result: running/done) |
| 语音播报 | `curl 'http://192.168.199.10:60010/skill-tts-chinese?content=TEXT'` |
| 显示表情 | `curl 'http://192.168.199.10:60010/skill-show-emotion?code=008'` |
| 拍照 | `curl 'http://192.168.199.10:60010/skill-take-photo?id=0'` |
| 录音 | `curl 'http://192.168.199.10:60010/skill-record?code=0'` |
| 显示图片 | `curl 'http://192.168.199.10:60010/skill-show-image' -F 'image=@/path'` |

## 动作与颜色参数
- **action**: 0=移动 1=取子 2=落子
- **color**: 1=黑 2=白

## 表情编号 code

code: 002=快乐 003=哭 004=默认 008=兴趣 011=摇头轻快 012=摇头否认 013=消失 014=出现

## 坐标

- 棋盘: (0,0)右上 → (12,12)左下
- 右棋盒: (-3.8,0) → (-1.8,7)
- 左棋盒: (14.2,0) → (15.8,7)

## 标准操作流程

```bash
# 1. 查找棋子
curl 'http://192.168.199.10:60010/skill-detect-box'
# 2. 根据返回坐标取子
curl 'http://192.168.199.10:60010/skill-move-tcp?x=X&y=Y&action=1'
# 3. 只有取子成功（"result": "success"）后，才落子到 (6,6)
curl 'http://192.168.199.10:60010/skill-move-tcp?x=6&y=6&action=2'
```
