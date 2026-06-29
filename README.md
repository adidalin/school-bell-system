<!--
  搜索关键词 / Search Keywords:
  钢城智慧铃声系统 校园广播系统 学校打铃系统 自动打铃 智能广播 校园铃声 上下课铃声 课间操铃声
  作息时间管理 学校铃声控制系统 多区域广播 定压功放 公共广播系统 PA系统
  School Bell System Campus Bell Automatic Bell Ringing School Schedule Bell
  Multi-zone Audio Broadcast Campus PA System Smart School Bell Timer
  上课铃 下课铃 预备铃 放学铃 紧急铃 起床铃 就寝铃 考试铃
  钉钉告警 节假日自动判断 NTP校时 网络校时 时间同步
  TTS语音合成 实时广播 组合铃声 预约铃声 Edge TTS 小米MiMo TTS
  Flask APScheduler SQLite Python广播系统 Windows广播服务器
  school bell scheduler campus audio management multi-zone bell controller
  dingtalk school notification holiday-aware bell system tts broadcast
  Gangcheng Smart Bell System
-->

<p align="center">
  <img src="https://img.shields.io/badge/Version-5.0-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.9+-green?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square" alt="Platform">
</p>

<h1 align="center">🔔 钢城智慧铃声系统</h1>
<h3 align="center">Gangcheng Smart Bell System — Multi-zone Campus Bell Scheduler</h3>

<p align="center">
  全 Web 架构 · 多区域独立课表 · 节假日自动判断 · NTP 精准校时 · 钉钉机器人告警 · TTS语音合成 · 实时广播 · 组合铃声 · 预约铃声
</p>

---

## 📖 目录

- [功能特性](#-功能特性)
- [系统架构](#-系统架构)
- [数据库设计](#-数据库设计)
- [API 接口](#-api-接口)
- [快速开始](#-快速开始)
- [配置说明](#-配置说明)
- [FAQ](#-faq)

---

## ✨ 功能特性

### 核心功能

| 功能 | 说明 |
|------|------|
| **多区域管理** | 支持A/B/C（教学楼/操场/宿舍楼）+ 自定义区域，每个区域独立控制 |
| **课表管理** | 多套课表（平日/考试），支持新建、激活、删除 |
| **打铃任务** | 每秒检查，精确到分钟触发，支持周几重复和一次性日期 |
| **多类型铃声** | 上课铃/下课铃/预备铃/课间操/午餐铃/放学铃/紧急铃/自定义 |
| **节假日管理** | 自动获取中国法定节假日，支持自定义节假日/调休 |
| **NTP校时** | 每日自动校准，支持直接设置系统时钟 |
| **钉钉告警** | 打铃异常告警、明日状态提醒、预约提醒 |

### V5.0 新增功能

| 功能 | 说明 |
|------|------|
| **TTS语音合成** | 支持 Edge TTS（微软）和 小米MiMo TTS，14+种音色可选 |
| **首页实时广播** | 最高优先级，打断当前播放，直接广播到指定区域 |
| **组合铃声** | 积木式组合：提示音 + TTS语音 + 正式铃声，顺序播放 |
| **提示音管理** | 上传/管理提示音文件，用于组合铃声前置音 |
| **预约铃声** | 为特定课表任务临时替换铃声，到期自动生效，过期自动恢复 |

---

## 🏗️ 系统架构

### 文件职责

```
钢城智慧铃声系统/
├── run.py                 # 启动入口：Flask + APScheduler + 初始化
├── app.py                 # Web API 路由（所有 /api/* 端点）
├── engine.py              # 核心引擎（BellEngine / NTPSync / AudioPlayer / DingTalkNotifier）
├── models.py              # SQLite 数据库（建表 + 自动迁移 + 日志/设置读写）
├── tts.py                 # TTS语音模块（Edge TTS + 小米MiMo TTS）
├── requirements.txt       # Python 依赖
├── templates/
│   ├── index.html         # 前端主界面（单页应用，约2100行）
│   └── login.html         # 登录界面
├── static/
│   ├── sounds/            # 铃声音频文件（.wav）
│   └── tts_cache/         # TTS缓存文件
├── data/                  # SQLite 数据库文件（自动创建）
├── logs/                  # 运行日志
└── backups/               # 数据库备份
```

### 模块依赖图

```
run.py (主进程)
  ├── Flask app (app.py)
  │     ├── /api/status          → engine.get_next_bell() / engine.get_zone_status()
  │     ├── /api/schedules       → models 读写 schedules + schedule_tasks
  │     ├── /api/today_control   → models 写 today_exceptions
  │     ├── /api/tomorrow_control→ models 写 tomorrow_overrides
  │     ├── /api/bell_schedules  → models 读写 bell_schedules
  │     ├── /api/bell/*          → engine.player (AudioPlayer)
  │     ├── /api/holidays        → engine.holiday (HolidayChecker)
  │     ├── /api/ntp/sync        → engine.ntp (NTPSync)
  │     ├── /api/dingtalk/test   → engine.dingtalk (DingTalkNotifier)
  │     ├── /api/tts/*           → tts.tts_manager (TTSManager)
  │     ├── /api/broadcast       → engine.broadcast() 实时广播
  │     ├── /api/overrides       → models 读写 task_overrides 预约铃声
  │     └── /api/logs            → models 读 logs
  ├── APScheduler
  │     ├── bell_check_task      → engine.check_and_ring()  每秒
  │     ├── ntp_sync_task        → engine.ntp.sync()         每日06:00
  │     ├── tomorrow_alert       → engine.check_tomorrow_and_alert()  每日08:00
  │     ├── bell_schedule_migrate→ engine.process_bell_schedules("migrate")  每日01:00
  │     └── status_log           → 状态日志                  每10分钟
  └── 启动初始化
        ├── init_db()            → 建表 + 自动迁移
        ├── _migrate_tomorrow_to_today()  → 明日覆盖→今日例外
        └── engine.process_bell_schedules("migrate")  → 预约→今日例外
```

---

## 🗄️ 数据库设计

共 11 张核心表，SQLite 存储于 `data/school_bell.db`：

| 表名 | 说明 |
|------|------|
| `zones` | 区域（教学楼/操场/宿舍楼等） |
| `schedules` | 课表方案 |
| `schedule_tasks` | 打铃任务（时间、铃声类型、适用日期） |
| `bells` | 铃声文件（普通铃声 + 组合铃声） |
| `bell_bindings` | 区域-铃声绑定 |
| `today_exceptions` | 今日例外（强制打铃/不打铃） |
| `tomorrow_overrides` | 明日覆盖 |
| `bell_schedules` | 预约控制（未来日期铃声开关） |
| `task_overrides` | 预约铃声（任务级临时换铃） |
| `custom_holidays` | 自定义节假日 |
| `settings` | 系统设置（KV存储） |
| `logs` | 运行日志 |

---

## 🔌 API 接口

基础路径：`http://host:8787`

### 系统状态
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/status` | 系统总览 |
| GET | `/api/health` | 健康检查 |

### 课表管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/schedules` | 课表列表 |
| POST | `/api/schedules` | 创建课表 |
| PUT | `/api/schedules/<id>` | 更新课表 |
| DELETE | `/api/schedules/<id>` | 删除课表 |

### 任务管理
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/tasks` | 添加任务 |
| GET | `/api/tasks/<id>` | 获取任务 |
| PUT | `/api/tasks/<id>` | 更新任务 |
| DELETE | `/api/tasks/<id>` | 删除任务 |

### 区域管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/zones` | 区域列表 |
| POST | `/api/zones` | 创建区域 |
| PUT | `/api/zones/<id>` | 更新区域 |
| DELETE | `/api/zones/<id>` | 删除区域 |

### 打铃控制
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/bell/ring` | 手动打铃 |
| POST | `/api/bell/pause` | 暂停 |
| POST | `/api/bell/resume` | 恢复 |
| POST | `/api/bell/stop` | 停止 |

### 今日/明日控制
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/today_control` | 今日控制（ring/no_ring/auto） |
| POST | `/api/tomorrow_control` | 明日控制 |

### 铃声管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/bells` | 铃声列表 |
| POST | `/api/bells/upload` | 上传铃声 |
| DELETE | `/api/bells/<id>` | 删除铃声 |
| POST | `/api/bell_bindings` | 更新绑定 |
| GET | `/api/prompts` | 提示音列表 |

### TTS语音
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tts/voices` | 音色列表 |
| POST | `/api/tts/preview` | 试听 |
| POST | `/api/tts/generate` | 生成TTS |
| GET/POST | `/api/tts/settings` | TTS设置 |
| POST | `/api/tts/test_xiaomi` | 检测小米API |

### 实时广播
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/broadcast` | 实时广播（最高优先级） |
| POST | `/api/broadcast/stop` | 停止广播 |

### 预约铃声
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/overrides` | 预约列表 |
| POST | `/api/overrides` | 创建预约 |
| DELETE | `/api/overrides/<id>` | 删除预约 |

### 预约控制
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/bell_schedules` | 预约控制列表 |
| POST | `/api/bell_schedules` | 创建预约控制 |
| DELETE | `/api/bell_schedules/<id>` | 删除预约控制 |

### 节假日
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/holidays` | 节假日列表 |
| POST | `/api/holidays/sync` | 同步节假日 |
| POST | `/api/holidays/custom` | 添加自定义节假日 |

### 系统设置
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/settings` | 获取设置 |
| POST | `/api/settings` | 保存设置 |
| POST | `/api/ntp/sync` | NTP校时 |
| POST | `/api/dingtalk/test` | 测试钉钉 |

### 其他
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/logs` | 运行日志 |
| GET | `/api/audio_devices` | 音频设备列表 |
| GET | `/api/export` | 导出课表Excel |
| POST | `/api/import` | 导入课表Excel |

---

## 🚀 快速开始

### 环境要求

- **Windows 10/11**（依赖 WASAPI 音频）
- **Python 3.9+**
- **VoiceMeeter Banana**（免费，用于多声卡路由）

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/adidalin/school-bell-system.git
   cd school-bell-system
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动系统**
   ```bash
   python run.py
   # 浏览器打开 http://127.0.0.1:8787
   ```

### 依赖列表

```
flask>=3.0
flask-apscheduler>=1.13
numpy>=1.26
sounddevice>=0.5
soundfile>=0.12
ntplib>=0.4
openpyxl>=3.1
pygame>=2.5
edge-tts>=7.0
```

---

## ⚙️ 配置说明

### TTS语音设置

系统支持两种TTS引擎：

| 引擎 | 音色数 | 费用 | 说明 |
|------|--------|------|------|
| Edge TTS（微软） | 14个 | 免费 | 无需API Key，本地运行 |
| 小米MiMo TTS | 8个 | 免费 | 需要API Key，高品质 |

**小米TTS音色列表：**
- 冰糖 (女) - 清甜明亮
- 茉莉 (女) - 温柔细腻
- Mia (女) - 优雅知性
- Chloe (女) - 甜美温柔
- 苏打 (男) - 清爽自然
- Milo (男) - 温暖磁性
- 白桦 (男) - 沉稳厚重
- Dean (男) - 浑厚低沉

**获取小米API Key：**
1. 访问 https://platform.xiaomimimo.com/console/api-keys
2. 创建账号并生成API Key
3. 在系统设置中输入API Key

### 钉钉告警配置

1. 打开钉钉群聊 → 右上角"..." → 群设置
2. 点击"智能群助手" → "添加机器人" → "自定义"
3. 安全设置选择"自定义关键词"，添加关键词"钢城智慧铃声"
4. 复制Webhook地址，粘贴到系统设置中

---

## ❓ FAQ

**Q: NTP校时失败怎么办？**
A: 需要管理员权限运行程序，或手动配置Windows时间服务。

**Q: 如何添加新区域？**
A: 在"区域控制"页面点击"+ 新增区域"，输入区域ID和名称。

**Q: 组合铃声是什么？**
A: 组合铃声可以将提示音、TTS语音、正式铃声按顺序播放，实现"叮咚 + 语音提示 + 铃声"的效果。

**Q: 预约铃声和今日控制有什么区别？**
A: 今日控制当天生效，预约铃声可提前任意天数设置，且支持任务级替换。

**Q: 如何备份数据？**
A: 系统每日凌晨2:30自动备份数据库到`backups/`目录，保留7天。

---

## 📄 License

MIT — 自由使用、修改、分发

---

<p align="center">
  <sub>Made with ❤️ for schools</sub>
</p>
