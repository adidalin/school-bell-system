<!--
  搜索关键词 / Search Keywords:
  校园广播系统 学校打铃系统 自动打铃 智能广播 校园铃声 上下课铃声 课间操铃声
  作息时间管理 学校铃声控制系统 多区域广播 定压功放 公共广播系统 PA系统
  School Bell System Campus Bell Automatic Bell Ringing School Schedule Bell
  Multi-zone Audio Broadcast Campus PA System Smart School Bell Timer
  上课铃 下课铃 预备铃 放学铃 紧急铃 起床铃 就寝铃 考试铃
  钉钉告警 节假日自动判断 NTP校时 网络校时 时间同步
  Flask APScheduler SQLite Python广播系统 Windows广播服务器
  school bell scheduler campus audio management multi-zone bell controller
  dingtalk school notification holiday-aware bell system
-->

<p align="center">
  <img src="https://img.shields.io/badge/Version-5.4-blue?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.9+-green?style=flat-square" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey?style=flat-square" alt="Platform">
</p>

<h1 align="center">🔔 校园智能广播定时系统</h1>
<h3 align="center">School Bell Smart Scheduling & Broadcast System</h3>

<p align="center">
  全 Web 架构 · 多区域独立课表 · 节假日自动判断 · NTP 精准校时 · 钉钉机器人告警 · 预约关铃控制
</p>

---

## 📖 目录

- [功能一览](#-功能一览)
- [界面预览](#-界面预览)
- [架构设计](#-架构设计)
- [硬件连接方案](#-硬件连接方案)
- [快速开始](#-快速开始)
- [部署指南](#-部署指南)
- [API 接口](#-api-接口)
- [定时任务](#-定时任务)
- [技术栈](#-技术栈)
- [FAQ](#-faq)

---

## 🎯 功能一览

### 核心功能

| 模块 | 功能描述 |
|------|---------|
| 🏠 **系统总览** | 按区域展示今日/明日打铃状态、下次打铃倒计时、NTP 校时状态、全局快捷控制 |
| 📋 **课表管理** | 多套课表方案并存、一键设为默认课表、按区域独立编排打铃任务、弹窗编辑、Excel 导入/导出/模板下载 |
| 🎚️ **区域控制** | 每个区域独立绑定课表、独立音量调节、独立音频设备选择（多声卡支持）、暂停/恢复/测试打铃 |
| 🔔 **铃声管理** | 12 种预设铃型、支持上传 MP3/WAV/OGG/M4A/AAC/FLAC/WMA、浏览器在线试听、按区域+铃型绑定自定义铃声 |
| 📅 **节假日** | 自动同步中国官方节假日（timor.tech API，可替换）、放假自动停铃/调休自动打铃、自定义日期手动切换 |
| 📆 **预约控制** | 预约未来任意日期+区域开关铃声、钉钉提前一天 8:00 自动提醒、可单独关闭/开启提醒 |
| ⚙️ **系统设置** | 密码保护、NTP 服务器配置、钉钉 Webhook 告警、节假日 API 源切换 |
| 📜 **运行日志** | 按类别筛选（打铃/手动/异常/系统/设置）、分页查看、实时记录 |

### 铃声类型

`上课铃` · `下课铃` · `预备铃` · `课间操` · `午餐铃` · `放学铃` · `紧急铃` · `起床铃` · `就寝铃` · `自定义`

---

## 🖥️ 界面预览

系统采用 **Ant Design 风格**暗色侧边栏 + 亮色内容区单页应用，7个功能页面

```
┌─────────────┬──────────────────────────────────────────┐
│  🔔 校园广播  │  系统总览                    ⏰ 12:30:45 │
│             │──────────────────────────────────────────│
│  ▸ 系统总览  │  ┌─ 今日状态 ──────────────────────────┐ │
│  课表管理    │  │ 教学楼 [正常打铃] 今日打铃 [▼默认] ...│ │
│  区域控制    │  │ 操  场 [正常打铃] 今日打铃 [▼默认] ...│ │
│  铃声管理    │  │ 宿舍楼 [正常打铃] 今日打铃 [▼默认] ...│ │
│  节假日      │  └──────────────────────────────────────┘ │
│  预约控制    │  ┌─ 明日状态 ──────────────────────────┐ │
│  系统设置    │  │ ...                                   │ │
│  运行日志    │  └──────────────────────────────────────┘ │
│             │  ┌──┐ ┌──┐ ┌──────┐ ┌──────┐             │
│  🟢 运行中   │  │课│ │运│ │下次打│ │NTP校 │             │
│             │  │表│ │行│ │铃时间│ │时状态│             │
└─────────────┴──────────────────────────────────────────┘
```

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                        run.py (启动入口)                      │
│  ┌──────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │ Flask Server │  │  APScheduler     │  │  初始化/迁移   │  │
│  │  (端口8787)  │  │  (定时任务调度)   │  │  (DB自检/NTP)  │  │
│  └──────┬───────┘  └────────┬─────────┘  └───────────────┘  │
└─────────┼───────────────────┼────────────────────────────────┘
          │                   │
    ┌─────▼─────┐       ┌─────▼──────────────┐
    │  app.py   │       │    engine.py        │
    │  API 路由  │       │  ┌────────────────┐ │
    │  · 状态    │       │  │ BellEngine     │ │
    │  · 课表    │       │  │ · 打铃调度      │ │
    │  · 区域    │       │  │ · 节假日判断    │ │
    │  · 铃声    │       │  │ · 预约控制      │ │
    │  · 节假日  │       │  │ · 钉钉告警      │ │
    │  · 预约    │       │  ├────────────────┤ │
    │  · 设置    │       │  │ NTPSync        │ │
    │  · 日志    │       │  │ · 3次测量中位数 │ │
    └─────┬──────┘       │  │ · 直接校时API   │ │
          │              │  ├────────────────┤ │
    ┌─────▼──────┐       │  │ AudioPlayer    │ │
    │ models.py  │       │  │ · 多设备独立播放│ │
    │ SQLite DB  │       │  │ · 区域音量控制  │ │
    │ · 6张核心表│       │  │ · 暂停/恢复     │ │
    │ · 自动迁移  │       │  └────────────────┘ │
    └────────────┘       └──────────────────────┘
```

### 课表优先级（打铃时判定）

```
1. 今日手动控制（today_exceptions）── 最高优先
   ↓ 无
2. 预约控制（bell_schedules 自动迁移）
   ↓ 无
3. 区域绑定课表（zone.schedule_id）
   ↓ 无
4. 系统默认课表（is_active=1）── 兜底
```

---

## 🔊 硬件连接方案

### 方案一：板载多声道声卡（0 元成本）

大多数台式机主板（Realtek ALC 系列）支持 5.1/7.1 声道，背板有 **3 个独立输出孔**：

```
🟢 绿色孔 (前置L/R) ── 3.5mm→RCA线 ── 功放1 ── 教学楼喇叭
⚫ 黑色孔 (后置L/R) ── 3.5mm→RCA线 ── 功放2 ── 操场喇叭
🟠 橙色孔 (中置/低音)── 3.5mm→RCA线 ── 功放3 ── 宿舍楼喇叭
```

**所需线材**：3.5mm 转双 RCA（莲花头）音频线，约 5 元/根

### 方案二：USB 外置声卡（≈30 元）

适用场景：主板只有一个输出孔、笔记本、需要更多区域

```
USB口1 ── USB声卡1 (≈10元) ── 3.5mm→RCA ── 功放1
USB口2 ── USB声卡2 (≈10元) ── 3.5mm→RCA ── 功放2
USB口3 ── USB声卡3 (≈10元) ── 3.5mm→RCA ── 功放3
```

每插入一个 USB 声卡，Windows 自动识别为一个独立播放设备，在系统「区域控制」页面分别选择即可。

### 功放连接

学校公共广播通常使用 **定压功放（70V/100V）**，喇叭并联在同一条广播线上。

- **输入端**：RCA 莲花头 / 凤凰端子（螺丝压接）
- **输出端**：110V/70V 定压输出，接定压喇叭
- **连接线**：3.5mm 转 RCA 线（电脑→功放），2芯纯铜广播线（功放→喇叭）

### 推荐清单

| 设备 | 数量 | 单价 | 用途 |
|------|------|------|------|
| USB 外置声卡 | 3 个 | ≈10 元 | 独立音频输出通道 |
| 3.5mm 转 RCA 线 | 3 根 | ≈5 元 | 连接声卡到功放 |
| 定压功放 | 3 台 | 按需 | 驱动各区域喇叭 |
| 定压喇叭 | 按需 | 按需 | 教室/走廊/操场广播 |

---

## 🚀 快速开始

### 环境要求

- **操作系统**：Windows 10/11 或 Linux（推荐 Windows）
- **Python**：3.9 及以上
- **内存**：2GB+ 可用
- **磁盘**：100MB（含铃声音频）

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/yourname/school-bell-system.git
cd school-bell-system

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动系统
python run.py
```

浏览器打开 `http://127.0.0.1:8787` 即可使用。

### 首次配置

1. 进入「系统设置」→ 设置管理密码（可选但推荐）
2. 进入「节假日」→ 点击「同步节假日」获取当年放假安排
3. 进入「课表管理」→ 新建课表 → 添加打铃任务 → 设为默认课表
4. 进入「区域控制」→ 为每个区域绑定课表和音频设备
5. 进入「预约控制」→ 提前设置特殊日期的铃声开关（如考试周关铃）

---

## 📦 部署指南

### Windows 开机自启

双击运行 `startup.bat`，自动将系统添加到开机启动文件夹。

**NTP 精准校时（可选）**：右键 `startup.bat` → **以管理员身份运行**，自动配置 Windows 时间服务与阿里云 NTP 同步。

系统以隐藏模式运行（`start_hidden.vbs` 启动 pythonw，无控制台窗口）。

### Linux systemd 服务

```bash
sudo cp school-bell.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable school-bell
sudo systemctl start school-bell
```

`Restart=always` 确保进程崩溃或断电重启后自动恢复。

### 断电自动恢复

- **Windows**：开机自启 + `start_hidden.vbs` 常驻
- **Linux**：systemd `Restart=always` + `RestartSec=5`

---

## 🔌 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/status` | 系统总览状态（含各区域今日/明日/下次打铃） |
| `GET/POST` | `/api/schedules` | 课表方案列表/创建 |
| `PUT/DELETE` | `/api/schedules/<id>` | 更新/删除课表（激活即设为默认） |
| `GET/POST` | `/api/tasks` | 获取/添加打铃任务 |
| `PUT/DELETE` | `/api/tasks/<id>` | 更新/删除任务 |
| `GET` | `/api/zones` | 区域列表（含绑定课表） |
| `PUT` | `/api/zones/<id>` | 更新区域（名称/音量/设备/课表） |
| `POST` | `/api/today_control` | 今日打铃控制（ring/no_ring/auto） |
| `POST` | `/api/tomorrow_control` | 明日打铃控制 |
| `GET/POST` | `/api/bell_schedules` | 预约控制列表/创建 |
| `PUT/DELETE` | `/api/bell_schedules/<id>` | 更新/删除预约 |
| `POST` | `/api/bell/ring` | 手动打铃 |
| `POST` | `/api/bell/pause\|resume\|stop` | 暂停/恢复/停止 |
| `GET` | `/api/bells` | 铃声库列表 |
| `POST` | `/api/bells/upload` | 上传自定义铃声 |
| `GET/POST` | `/api/holidays` | 节假日列表/同步 |
| `GET/POST` | `/api/settings` | 系统设置读写 |
| `POST` | `/api/ntp/sync` | 手动触发 NTP 校时 |
| `GET` | `/api/logs` | 运行日志（分页/分类） |
| `GET` | `/api/health` | 健康检查 |

---

## ⏰ 定时任务

| 任务 | 频率 | 说明 |
|------|------|------|
| 🔔 打铃检查 | **每秒** | 匹配时间触发各区域打铃 |
| 🕐 NTP 校时 | 每日 06:00 + 每小时 | 3 次测量取中位数，偏差 >0.2s 自动校准 |
| 📅 节假日获取 | 每月 1 日 02:00 | 自动拉取新一年官方节假日 |
| 📢 明日提醒 | 每日 **08:00** | 检查明日状态+预约控制，统一钉钉告警 |
| 🔄 预约迁移 | 每日 01:00 | 当天预约自动转为今日例外执行 |
| 📊 状态日志 | 每 10 分钟 | 记录系统健康状态 |

---

## 🛠️ 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **后端框架** | Python Flask | Web API 服务 |
| **任务调度** | APScheduler | 定时打铃/校时/提醒/预约迁移 |
| **数据库** | SQLite + 自动迁移 | 6 张核心业务表 |
| **前端** | 原生 HTML/CSS/JavaScript | 单页应用，Ant Design 风格，零依赖 |
| **音频播放** | pygame mixer | 多设备独立混音播放 |
| **网络校时** | ntplib + Win32 API | 3 次测量中位数 + SetSystemTime 直接校准 |
| **Excel 处理** | openpyxl | 课表导入/导出/模板 |
| **钉钉通知** | HTTP POST Webhook | 异常告警 + 预约提醒 |
| **节假日** | timor.tech API | 中国官方节假日（可替换） |

---

## ❓ FAQ

**Q: 为什么 NTP 校时总是显示 0.x 秒偏差？**
A: NTP 测量会受网络延迟影响（约 10-50ms 抖动），系统已用 3 次测量取中位数消抖。校准需管理员权限，请以管理员身份运行 `startup.bat` 一次配置 Windows 时间服务即可实现高精度同步。

**Q: 如何让三个区域同时播放不同铃声？**
A: 使用 3 个 USB 声卡或板载多声道声卡，在「区域控制」页面为每个区域选择不同音频输出设备。

**Q: 断电重启后会自动恢复吗？**
A: 会。Windows 上 `startup.bat` 配置的开机自启 + `start_hidden.vbs` 确保登录后自动运行；Linux 上 systemd `Restart=always` 确保自动恢复。

**Q: 可以远程管理吗？**
A: 可以。系统监听 `0.0.0.0:8787`，局域网内任何设备均可通过浏览器访问。建议设置密码保护。

**Q: 预约关铃和今日控制的区别？**
A: 今日控制是临时操作（仅当天有效），预约控制可以提前设置未来任意日期的铃声开关，并提前一天 8:00 钉钉提醒。

---

## 📄 License

MIT License - 自由使用、修改、分发

---

<p align="center">
  <sub>Made with ❤️ for schools everywhere</sub>
</p>
