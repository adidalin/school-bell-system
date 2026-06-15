<!--
  搜索关键词 / Search Keywords:
  钢城智慧铃声系统 校园广播系统 学校打铃系统 自动打铃 智能广播 校园铃声 上下课铃声 课间操铃声
  作息时间管理 学校铃声控制系统 多区域广播 定压功放 公共广播系统 PA系统
  School Bell System Campus Bell Automatic Bell Ringing School Schedule Bell
  Multi-zone Audio Broadcast Campus PA System Smart School Bell Timer
  上课铃 下课铃 预备铃 放学铃 紧急铃 起床铃 就寝铃 考试铃
  钉钉告警 节假日自动判断 NTP校时 网络校时 时间同步
  Flask APScheduler SQLite Python广播系统 Windows广播服务器
  school bell scheduler campus audio management multi-zone bell controller
  dingtalk school notification holiday-aware bell system
  Gangcheng Smart Bell System
-->

<p align="center">
  <img src="https://img.shields.io/badge/Version-5.4-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.9+-green?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey?style=flat-square" alt="Platform">
</p>

<h1 align="center">🔔 钢城智慧铃声系统</h1>
<h3 align="center">Gangcheng Smart Bell System — Multi-zone Campus Bell Scheduler</h3>

<p align="center">
  全 Web 架构 · 多区域独立课表 · 节假日自动判断 · NTP 精准校时 · 钉钉机器人告警 · 预约关铃控制
</p>

---

## 📖 目录

- [系统架构](#-系统架构)
- [数据库设计](#-数据库设计)
- [API 接口](#-api-接口)
- [定时任务](#-定时任务)
- [核心逻辑](#-核心逻辑)
- [硬件连接方案](#-硬件连接方案)
- [快速开始](#-快速开始)
- [部署指南](#-部署指南)
- [配置说明](#-配置说明)
- [FAQ](#-faq)

---

## 🏗️ 系统架构

### 文件职责

```
school-bell-v4/
├── run.py                 # 启动入口：Flask + APScheduler + 初始化
├── app.py                 # Web API 路由（所有 /api/* 端点）
├── engine.py              # 核心引擎（BellEngine / NTPSync / AudioPlayer / DingTalkNotifier）
├── models.py              # SQLite 数据库（建表 + 自动迁移 + 日志/设置读写）
├── requirements.txt       # Python 依赖
├── install.bat            # Windows 一键安装（装依赖 + 开机自启 + NTP配置）
├── startup.bat            # 开机自启配置 + NTP时间服务配置
├── start_hidden.vbs       # VBS 隐藏窗口启动器
├── school-bell.service    # Linux systemd 服务文件
├── templates/
│   ├── index.html         # 前端主界面（单页应用，7个页面）
│   └── login.html         # 登录界面
├── static/sounds/         # 铃声音频文件（.wav/.mp3）
├── data/                  # SQLite 数据库文件（自动创建，不入 git）
├── logs/                  # 运行日志（自动创建，不入 git）
└── backups/               # 课表备份（不入 git）
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

共 9 张核心表，SQLite 存储于 `data/school_bell.db`：

### schedules（课表方案）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | 自增主键 |
| name | TEXT | 课表名称（如"平日课表""周末课表"） |
| is_active | INTEGER | 是否系统默认课表（1=是，全局唯一） |

> 激活课表时清空其他课表的 is_active，保证全局只有一个默认。

### schedule_tasks（打铃任务）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| schedule_id | INTEGER FK | 所属课表 |
| zone_id | TEXT | 区域ID（A/B/C/ALL） |
| time | TEXT | 时间（HH:MM 格式） |
| bell_type | TEXT | 铃声类型（class_start/class_end/prepare/...） |
| task_name | TEXT | 任务名称 |
| days | TEXT | 适用星期（"1,2,3,4,5"=工作日） |
| one_time_date | TEXT | 一次性日期（非空则该任务仅当日执行） |
| bell_id | INTEGER | 绑定的自定义铃声ID（0=使用默认） |

### zones（区域）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 区域ID（A/B/C） |
| name | TEXT | 显示名称（教学楼/操场/宿舍楼） |
| enabled | INTEGER | 是否启用 |
| volume | REAL | 音量（0.0~1.0） |
| audio_device | TEXT | 音频输出设备名（空=默认设备） |
| schedule_id | INTEGER | 绑定的默认课表（0=跟随系统默认） |
| sort_order | INTEGER | 排序 |

### today_exceptions（今日例外）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| date | TEXT | 日期（YYYY-MM-DD） |
| zone_id | TEXT | 区域ID |
| action | TEXT | force_ring（强制打铃）/ force_no_ring（强制不打铃） |
| reason | TEXT | 原因说明 |
| schedule_id | INTEGER | 强制打铃时使用的课表ID |
| created_at | TEXT | 创建时间 |

### tomorrow_overrides（明日覆盖）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| date | TEXT | 明天日期 |
| zone_id | TEXT | 区域ID |
| action | TEXT | force_ring / force_no_ring |
| schedule_id | INTEGER | 课表ID |
| reason | TEXT | 原因 |
| created_at | TEXT | 创建时间 |

> 每日启动时 `_migrate_tomorrow_to_today()` 将 date=今日 的记录迁入 today_exceptions，并删除旧记录。

### bell_schedules（预约控制）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| date | TEXT | 预约日期 |
| zone_id | TEXT | 区域ID |
| action | TEXT | force_ring / force_no_ring |
| schedule_id | INTEGER | 课表ID（打铃时用） |
| reason | TEXT | 原因说明 |
| remind_enabled | INTEGER | 是否发送提醒（1=是） |
| remind_at | TEXT | 提醒时间（默认"20:00"，预留） |
| reminded | INTEGER | 是否已提醒（防重复） |
| created_at | TEXT | 创建时间 |

> UNIQUE(date, zone_id) — 同一天同一区域只能有一条预约。每日 01:00 自动迁移当天预约到 today_exceptions。

### bells / bell_bindings（铃声库 + 绑定）
| 表 | 关键字段 | 说明 |
|------|------|------|
| bells | id, name, filename, bell_type, duration | 铃声文件元信息 |
| bell_bindings | zone_id, bell_type, bell_id | 区域+铃型→铃声文件映射 |

### custom_holidays（自定义节假日）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| date | TEXT | 日期 |
| name | TEXT | 节日名称 |
| is_holiday | INTEGER | 1=放假(不打铃) / 0=调休(打铃) |

### settings（系统设置，KV 存储）
| Key | 说明 | 默认值 |
|------|------|------|
| password | MD5 密码 | 空（无密码） |
| ntp_server | NTP 服务器 | ntp.aliyun.com |
| ntp_enabled | NTP 开关 | 1 |
| ntp_last_sync | 上次校时时间 | 空 |
| dingtalk_webhook | 钉钉 Webhook URL | 空 |
| dingtalk_enabled | 钉钉开关 | 0 |
| holiday_api_url | 节假日 API | https://timor.tech/api/holiday/year/{} |

### logs（运行日志）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER PK | |
| timestamp | TEXT | 时间戳 |
| level | TEXT | INFO/WARNING/ERROR |
| category | TEXT | system/schedule/exception/bell/settings/import/zone |
| message | TEXT | 日志内容 |

---

## 🔌 API 接口

基础路径：`http://host:8787`

### 系统状态
| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| GET | `/api/status` | 系统总览 | 无 |
| GET | `/api/health` | 健康检查 | 无 |

### 课表管理
| 方法 | 路径 | 说明 | 关键参数 |
|------|------|------|------|
| GET | `/api/schedules` | 课表列表（含每个课表的任务按区域分组） | 无 |
| POST | `/api/schedules` | 创建课表 | `{name}` |
| PUT | `/api/schedules/<id>` | 更新课表（name或activate=true） | `{name}` 或 `{activate:true}` |
| DELETE | `/api/schedules/<id>` | 删除课表（激活中不可删） | 无 |

### 任务管理
| 方法 | 路径 | 说明 | 关键参数 |
|------|------|------|------|
| POST | `/api/tasks` | 添加任务 | `{schedule_id, zone_id, time, bell_type, task_name, days, one_time_date, bell_id}` |
| GET | `/api/tasks/<id>` | 获取单个任务 | 无 |
| PUT | `/api/tasks/<id>` | 更新任务 | 同 POST，部分字段可选 |
| DELETE | `/api/tasks/<id>` | 删除任务 | 无 |

### 区域管理
| 方法 | 路径 | 说明 | 关键参数 |
|------|------|------|------|
| GET | `/api/zones` | 区域列表（含 schedule_id、播放状态） | 无 |
| PUT | `/api/zones/<zone_id>` | 更新区域 | `{name, volume(0-100), audio_device, enabled, schedule_id}` |

### 打铃控制
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/bell/ring` | 手动打铃 `{zone_id, bell_type}` |
| POST | `/api/bell/pause` | 暂停 `{zone_id?}`（空=全局） |
| POST | `/api/bell/resume` | 恢复 `{zone_id?}` |
| POST | `/api/bell/stop` | 停止 `{zone_id?}` |

### 今日/明日控制
| 方法 | 路径 | 说明 | 参数 |
|------|------|------|------|
| POST | `/api/today_control` | 今日控制 | `{zone_id, action(ring/no_ring/auto), schedule_id?}` |
| POST | `/api/tomorrow_control` | 明日控制 | `{zone_id, action, schedule_id?}` |
| GET | `/api/today_exceptions` | 今日例外列表 | `?date=YYYY-MM-DD` |

### 预约控制
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/bell_schedules` | 预约列表 `?date=YYYY-MM-DD` |
| POST | `/api/bell_schedules` | 创建预约 `{date, zone_id, action, schedule_id, reason, remind_enabled}` |
| PUT | `/api/bell_schedules/<id>` | 更新预约 |
| DELETE | `/api/bell_schedules/<id>` | 删除预约 |

### 铃声管理
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/bells` | 铃声列表（含 bindings） |
| POST | `/api/bells/upload` | 上传铃声（multipart: file + name + bell_type） |
| DELETE | `/api/bells/<id>` | 删除铃声（同时删文件+binding） |
| POST | `/api/bell_bindings` | 更新绑定 `{zone_id, bell_type, bell_id}` |

### 节假日
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/holidays` | 节假日列表 `?year=` |
| POST | `/api/holidays/sync` | 强制同步当年节假日 |
| POST | `/api/holidays/custom` | 添加自定义节假日 `{date, name, is_holiday}` |
| PUT | `/api/holidays/custom/<id>` | 切换打铃/不打铃 |
| DELETE | `/api/holidays/custom/<id>` | 删除自定义节假日 |

### 系统设置
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/settings` | 读取所有设置（不含密码） |
| POST | `/api/settings` | 写入设置（KV 对） |
| POST | `/api/ntp/sync` | 手动触发 NTP 校时 |
| POST | `/api/dingtalk/test` | 测试钉钉消息（绕过冷却） |

### 课表导入导出
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/export` | 导出课表为 Excel `?schedule_id=` |
| GET | `/api/template` | 下载 Excel 模板 |
| POST | `/api/import` | 导入 Excel（multipart: file + schedule_name） |

### 其他
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/logs` | 运行日志 `?page=&per_page=&category=` |
| GET | `/api/audio_devices` | 可用音频设备列表 |
| POST | `/api/login` | 登录 `{password}` |

---

## ⏰ 定时任务

| 任务 | Cron | 说明 |
|------|------|------|
| bell_check_task | 每秒 | `engine.check_and_ring()` — 匹配时间触发打铃 |
| ntp_sync_task | 每日 06:00 | `engine.ntp.sync()` — 3 次测量取中位数 + SetSystemTime 直接校准 |
| tomorrow_alert | 每日 **08:00** | `engine.check_tomorrow_and_alert()` — 检查明日状态 + 预约控制，钉钉统一提醒 |
| bell_schedule_migrate | 每日 **01:00** | `engine.process_bell_schedules("migrate")` — 当天预约 → today_exceptions |
| status_log | 每 10 分钟 | 记录系统运行状态到日志 |

---

## 🧠 核心逻辑

### 打铃判定流程

```
check_and_ring() 每秒执行
  │
  ├── 获取当前 HH:MM
  ├── 遍历所有 enabled zones
  │     │
  │     ├── 1. 查 today_exceptions
  │     │     ├── force_no_ring → 跳过此区域
  │     │     └── force_ring → 使用指定 schedule_id
  │     │
  │     ├── 2. _get_zone_schedule() 确定课表
  │     │     优先级: today_exception.schedule_id > zone.schedule_id > 全局 is_active
  │     │
  │     ├── 3. 查 schedule_tasks 匹配当前时间
  │     │     过滤条件: zone_id==A/ALL, time==HH:MM, days含今天星期
  │     │
  │     ├── 4. 节假日判断 (HolidayChecker)
  │     │     today_exception 不受节假日影响
  │     │     否则: 放假→跳过, 调休→正常打铃
  │     │
  │     ├── 5. 播放铃声
  │     │     查 bell_bindings 获取该区域+铃型的自定义铃声文件
  │     │     AudioPlayer.play(zone_id, file)
  │     │
  │     └── 6. 检测播放异常 → 钉钉告警
  │
  └── 检查遗漏任务（该打没打的）→ 钉钉告警
```

### NTP 校时流程

```
NTPSync.sync()
  │
  ├── 取 3 次 NTP 测量 → 排序取中位数（消抖）
  ├── 偏移 > 0.2s 时：
  │     ├── _set_system_time_direct() — 启用 SeSystemtimePrivilege + SetSystemTime API
  │     │     └── 成功后二次测量验证
  │     └── _configure_w32time() — 兜底：配置 Windows 时间服务自动同步
  └── 偏移 ≤ 0.2s：仅记录
```

### 钉钉通知规范

消息格式：`msgtype: markdown`
- `title`: "钢城智慧铃声-{具体标题}"
- `text`: "### 钢城智慧铃声系统 - {标题}\n\n{内容}\n\n> 时间: ..."

防重复：同标题+内容前缀 30 分钟内不重发（测试接口 `bypass_cooldown=True`）

---

## 🔊 硬件连接方案

### 方案一：板载多声道声卡（0 元成本）

大多数台式机主板（Realtek ALC 系列）支持 5.1/7.1 声道，背板有 3 个独立输出孔：

```
🟢 绿色孔 (前置L/R) ── 3.5mm→RCA线 ── 功放1 ── 教学楼喇叭
⚫ 黑色孔 (后置L/R) ── 3.5mm→RCA线 ── 功放2 ── 操场喇叭
🟠 橙色孔 (中置/低音)── 3.5mm→RCA线 ── 功放3 ── 宿舍楼喇叭
```

所需线材：3.5mm 转双 RCA（莲花头）音频线，约 5 元/根

### 方案二：USB 外置声卡（≈30 元）

```
USB口1 ── USB声卡1 (≈10元) ── 3.5mm→RCA ── 功放1
USB口2 ── USB声卡2 (≈10元) ── 3.5mm→RCA ── 功放2
USB口3 ── USB声卡3 (≈10元) ── 3.5mm→RCA ── 功放3
```

每插入一个 USB 声卡，Windows 自动识别为独立播放设备，在「区域控制」页面分别选择即可。

### 功放连接

学校公共广播通常使用**定压功放（70V/100V）**：
- **输入端**：RCA 莲花头 / 凤凰端子（螺丝压接）
- **输出端**：110V/70V 定压输出，接定压喇叭（并联）
- **连接线**：3.5mm 转 RCA（电脑→功放），2芯纯铜广播线（功放→喇叭）

---

## 🚀 快速开始

### 环境要求
- Windows 10/11 或 Linux — Python 3.9+ — 2GB+ 内存 — 100MB 磁盘

### 安装启动

```bash
pip install -r requirements.txt
python run.py
# 浏览器打开 http://127.0.0.1:8787
```

### 首次配置顺序
1. 系统设置 → 设密码（可选）
2. 节假日 → 同步节假日
3. 课表管理 → 新建课表 → 添加任务 → 设为默认
4. 区域控制 → 绑定课表 + 音频设备
5. 预约控制 → 设置特殊日期（考试周关铃等）
6. 系统设置 → 配置钉钉 Webhook（需先在钉钉群创建机器人，安全设置选"自定义关键词"，填"钢城智慧铃声"）

---

## 📦 部署

### Windows 开机自启
双击 `startup.bat` 即可。如需 NTP 精准校时，右键 → 以管理员身份运行。

### Linux systemd
```bash
sudo cp school-bell.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now school-bell
```

---

## 🛠️ 技术栈

| 层 | 技术 | 用途 |
|------|------|------|
| 后端框架 | Python Flask | Web API |
| 任务调度 | APScheduler | 定时打铃/校时/提醒 |
| 数据库 | SQLite | 零配置本地存储 |
| 前端 | 原生 HTML/CSS/JS | 单页应用，Ant Design 风格，零依赖 |
| 音频 | pygame mixer | 多设备独立混音 |
| NTP | ntplib + Win32 API | 3 次测量中位数 + SetSystemTime |
| Excel | openpyxl | 课表导入导出 |
| 钉钉 | HTTP POST Webhook | markdown 消息推送 |
| 节假日 | timor.tech API | 中国官方节假日（可替换） |

---

## ❓ FAQ

**Q: NTP 偏差为什么有时 0.x 秒？**
A: 3 次测量取中位数消抖，偏移 >0.2s 自动调用 SetSystemTime 校准（需管理员权限）。打铃精度 1 秒内完全够用。

**Q: 三区域同时不同铃声怎么实现？**
A: 3 个 USB 声卡或板载多声道声卡，区域控制页分别选不同设备。

**Q: 预约关铃和今日控制有什么区别？**
A: 今日控制当天生效，预约控制可提前任意天数设置，且提前一天 8:00 钉钉提醒。

**Q: 钉钉测试返回 false？**
A: 可能是 30 分钟冷却期。系统自动提醒正常发送，只是连续测试会被冷却。

**Q: 断电重启后会自动恢复吗？**
A: Windows 上 startup.bat 配置的开机自启 + start_hidden.vbs 确保登录后自动运行。

---

## 📄 License

MIT — 自由使用、修改、分发

---

<p align="center"><sub>Made for schools, by schools</sub></p>
