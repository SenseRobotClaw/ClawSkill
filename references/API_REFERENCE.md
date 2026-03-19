# 元萝卜下棋机器人 API 参考文档

## 连接信息

- **IP 地址**: `192.168.199.10`
- **HTTP API 端口**: `60010`

---

## 📐 坐标系统

### 1. 棋盘坐标 (x, y)

| 位置 | 坐标 |
| :--- | :--- |
| **右上角** | `(0, 0)` |
| **左下角** | `(12, 12)` |

### 2. 棋盒坐标 (x, y)

| 棋盒 | 右上角 | 左下角 |
| :--- | :--- | :--- |
| **右棋盒** | `(-3.8, 0)` | `(-1.8, 7)` |
| **左棋盒** | `(14.2, 0)` | `(15.8, 7)` |

## 📡 指令控制方式

该机器人系统运行 Linux，内部搭建了 HTTP Server。你可以通过 `curl` 访问该元萝卜机器人，调用对应的控制指令。

- **基础地址**: `http://192.168.199.10:60010`

---

## 🛠️ 具体功能指令

### 1. 机械臂复位

将机械臂从棋盘上移开。

- **指令**:
  ```bash
  curl --location 'http://192.168.199.10:60010/skill-move-home'
  ```
- **参数**: 无
- **返回值**:
  ```json
  {
      "ok": true,
      "cmd": "skill-move-home",
      "result": "success|fail"
  }
  ```

### 2. 机械臂控制

操作机械臂到指定的 `x` 和 `y` 坐标位置去执行某一个 `action` 的动作。

- **指令**:
  ```bash
  curl --location 'http://192.168.199.10:60010/skill-move-tcp?x={x}&y={y}&action={action}'
  ```
- **参数**:
    - `x`: 横坐标
    - `y`: 纵坐标
    - `action`: 机械臂具体动作（`0`: 移动, `1`: 取子, `2`: 落子）
- **返回值**:
  ```json
  {
      "ok": true,
      "cmd": "skill-move-tcp",
      "result": "success|empty_put|catch_fail|full_catch|out_of_range|collision|fail_xxx",
      "x": 6,
      "y": 4,
      "action": 2
  }
  ```

### 3. 语音播报

控制机器人将 `content` 转为语音进行播放。

- **指令**:
  ```bash
  curl --location 'http://192.168.199.10:60010/skill-tts-chinese?content={content}'
  ```
- **参数**:
    - `content`: 仅限中文内容
- **返回值**:
  ```json
  {
      "ok": true,
      "cmd": "skill-tts-chinese",
      "result": "success|fail_empty_content"
  }
  ```

### 4. 看当前棋盘状态

进行棋盘分类和定位。**注意：在同一个棋盘下有且仅需要做一次。**

- **指令**:
  ```bash
  curl --location 'http://192.168.199.10:60010/skill-look-board'
  ```
- **参数**: 无
- **返回值**:
  ```json
  {
      "ok": true,
      "cmd": "skill-look-board",
      "result": "GO_BOARD_9" // GO_BOARD_19, GO_BOARD_13, GO_BOARD_9, CHINESE_CHECKERS, INTERNATIONAL_CHECKERS_8, INTERNATIONAL_CHECKERS_10, CHINESE_CHESS, INTERNATIONAL_CHESS, NIEDAO_BOARD_19, NIEDAO_BOARD_15, GAME_NONE, GAME_NUM
  }
  ```

### 5. 清理棋盘

把棋盘上的子收回棋盒。由于清理过程可能需要几分钟，此接口为异步调用，客户端需要通过轮询该接口来获取清理进度。

- **指令**:
  ```bash
  curl --location 'http://192.168.199.10:60010/skill-clean-board'
  ```
- **参数**: 无
- **返回值**:
  ```json
  {
      "ok": true,
      "cmd": "skill-clean-board",
      "started_at": "2024-03-19 12:00:00",
      "result": "running|done|error",
      "detail": "清理棋盘任务已开始，预计耗时约 3-5 分钟"
  }
  ```

### 6. 查找棋盒棋子的位置

使用 CV 能力从棋盒中准确检测棋子的位置。

- **指令**:
  ```bash
  curl --location 'http://192.168.199.10:60010/skill-detect-box'
  ```
- **参数**: 无
- **返回值**:
  ```json
  {
      "ok": true,
      "cmd": "skill-detect-box",
      "result": "success|fail_no_piece",
      "pieces": [
          {
              "color": 1,
              "x": -3.130963087081909,
              "y": 1.56145179271698
          }
      ]
  }
  ```
  *说明：`pieces` 数组中的 `color` 表示棋子颜色（1黑，2白），`x` 和 `y` 表示在棋盘坐标系下的具体坐标。如果未检测到棋子，`ok` 为 `false`，`result` 为 `"fail_no_piece"`，`pieces` 为空数组 `[]`。*

### 7. 查找棋盘棋子的位置

使用 CV 能力从棋盘中准确检测棋子的位置。

- **指令**:
  ```bash
  curl --location 'http://192.168.199.10:60010/skill-detect-board'
  ```
- **参数**: 无
- **返回值**:
  ```json
  {
      "ok": true,
      "cmd": "skill-detect-board",
      "result": "success|fail_no_piece",
      "pieces": [
          {
              "color": 1,
              "x": 3,
              "y": 4
          }
      ]
  }
  ```
  *说明：`pieces` 数组中的 `color` 表示棋子颜色（1黑，2白），`x` 和 `y` 表示在棋盘坐标系下的具体坐标。如果未检测到棋子，`ok` 为 `false`，`result` 为 `"fail_no_piece"`，`pieces` 为空数组 `[]`。*

### 8. 显示表情

控制机器人的屏幕显示一个表情。

- **指令**:
  ```bash
  curl --location 'http://192.168.199.10:60010/skill-show-emotion?code={code}'
  ```
- **参数**:
    - `code`: 表情数字编号
      | 编号 | 表情 | 编号 | 表情 |
      | :--- | :--- | :--- | :--- |
      | `002` | 快乐 | `011` | 摇头轻快 |
      | `003` | 哭 | `012` | 摇头否认 |
      | `004` | 默认 | `013` | 消失 |
      | `008` | 兴趣 | `014` | 出现 |
- **返回值**:
  ```json
  {
      "ok": true,
      "cmd": "skill-show-emotion",
      "result": "success|fail_empty_code"
  }
  ```

### 9. 拍照

控制机器人的任意一个摄像头拍照。

- **指令**:
  ```bash
  curl --location 'http://192.168.199.10:60010/skill-take-photo?id={id}'
  ```
- **参数**:
    - `id`: 摄像头编号
      | 编号 | 描述 |
      | :--- | :--- |
      | `0` | 前置人脸摄像头 |
      | `1` | 右边棋盘摄像头 |
      | `2` | 左边棋盘摄像头 |
- **返回值**: JPEG图片二进制数据

### 10. 录音

控制机器人的麦克风录音。

- **指令**:
  ```bash
  curl --location 'http://192.168.199.10:60010/skill-record?code={code}'
  ```
- **参数**:
    - `code`: 录音指令
      | 编号 | 描述 |
      | :--- | :--- |
      | `0` | 开始录音 |
      | `1` | 结束录音 |
- **返回值**:
    - 开始录音 (`code=0`): `skill-record success` (纯文本)
    - 结束录音 (`code=1`): PCM音频二进制数据(采样率:16000; 声道:单通道)

### 11. 显示图片

控制机器人的屏幕显示一张图片。

- **指令**:
  ```bash
  curl --location 'http://192.168.199.10:60010/skill-show-image' --form 'image=@"/C:/Users/Pictures/xxx.png"'
  ```
- **参数**:
    - `image`: 图片地址。注意：只支持png格式的图片
- **返回值**: `skill-show-image success`

---

## 🚨 错误处理与策略

### 落子失败（未吸子）

- **现象**: `skill-move-tcp` 执行 `action=2` 返回 `"result": "empty_put"`
- **原因**: 未吸子却尝试落子
- **处理**: 必须先确保 `action=1` 吸子成功（`"result": "success"`）后，才能执行 `action=2` 落子

### 取子失败重试策略

1. 调用 `skill-detect-box` 获取棋盒中棋子的坐标缓存
2. 遍历缓存中的坐标尝试取子。不管取子成功还是失败，都需要从缓存中移除该位置。若取子失败，就用缓存的下个位置重试
3. 如果所有缓存坐标都尝试失败，语音提示用户，并结束本次取子流程
