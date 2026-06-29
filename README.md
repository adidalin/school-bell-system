<!--
  🔍 搜索关键词 / Search Keywords:
  
  中文关键词:
  钢城智慧铃声系统 校园广播系统 学校打铃系统 自动打铃 智能广播 校园铃声 上下课铃声 课间操铃声
  作息时间管理 学校铃声控制系统 多区域广播 定压功放 公共广播系统 PA系统
  上课铃 下课铃 预备铃 放学铃 紧急铃 起床铃 就寝铃 考试铃
  课表管理 排课系统 打铃时间表 铃声定时 广播定时 自动打铃软件
  TTS语音合成 文字转语音 实时广播 组合铃声 预约铃声 提示音
  钉钉告警 节假日自动判断 NTP校时 网络校时 时间同步
  Edge TTS 微软语音 小米MiMo TTS AI语音合成
  
  英文关键词:
  School Bell System Campus Bell Automatic Bell Ringing School Schedule Bell
  Multi-zone Audio Broadcast Campus PA System Smart School Bell Timer
  school bell scheduler campus audio management multi-zone bell controller
  dingtalk school notification holiday-aware bell system
  TTS Text-to-Speech Real-time Broadcast Composite Bell Scheduled Bell
  Edge TTS Microsoft Voice Xiaomi MiMo TTS AI Voice Synthesis
  Flask APScheduler SQLite Python Bell System Windows Server
  
  技术栈:
  Python Flask SQLite APScheduler sounddevice soundfile numpy
  Edge-TTS MiMo-TTS Web API RESTful SPA Single Page Application
-->

<p align="center">
  <img src="https://img.shields.io/badge/Version-5.0-blue?style=flat-square&logo=git" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.9+-green?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square&logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/TTS-Edge%20%7C%20MiMo-orange?style=flat-square" alt="TTS">
</p>

<h1 align="center">🔔 钢城智慧铃声系统</h1>
<h3 align="center">Gangcheng Smart Bell System</h3>
<p align="center">🎓 专业的校园广播定时系统 · 多区域独立控制 · AI语音合成 · 智能调度</p>

<p align="center">
  <a href="#-功能特性">功能特性</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-版本历史">版本历史</a> •
  <a href="#-api文档">API文档</a> •
  <a href="#-faq">FAQ</a>
</p>

---

## 📋 项目简介

**钢城智慧铃声系统**是一款专为学校设计的智能广播定时系统，支持多区域独立控制、自动打铃、TTS语音合成、实时广播等功能。

🎯 **核心价值**：让学校铃声管理从手动操作升级为智能化自动运行，节省人力成本，提升管理效率。

### 🏫 适用场景

- 🏫 中小学、高中校园广播
- 🏢 培训机构定时提醒
- 🏭 工厂定时广播
- 🏥 医院定时提醒
- 🏠 任何需要定时音频播放的场景

---

## ✨ 功能特性

### 🎯 核心功能

| 功能 | 说明 | 状态 |
|------|------|------|
| 🔔 **多区域管理** | 支持A/B/C（教学楼/操场/宿舍楼）+ 自定义区域 | ✅ |
| 📅 **课表管理** | 多套课表（平日/考试），支持新建、激活、删除 | ✅ |
| ⏰ **智能打铃** | 每秒检查，精确到分钟，支持周几重复和一次性日期 | ✅ |
| 🎵 **多类型铃声** | 上课铃/下课铃/预备铃/课间操/午餐铃/放学铃/紧急铃 | ✅ |
| 📆 **节假日管理** | 自动获取中国法定节假日，支持自定义节假日/调休 | ✅ |
| 🕐 **NTP校时** | 每日自动校准，确保时间精准 | ✅ |
| 📱 **钉钉告警** | 打铃异常告警、明日状态提醒、预约提醒 | ✅ |
| 📊 **Excel导入导出** | 课表可导入/导出Excel，支持模板下载 | ✅ |
| 🔒 **密码保护** | 可选的访问密码保护 | ✅ |
| 💾 **自动备份** | 每日自动备份数据库，保留7天 | ✅ |

### 🆕 V5.0 新增功能

| 功能 | 说明 | 状态 |
|------|------|------|
| 🗣️ **TTS语音合成** | 支持 Edge TTS（微软）和 小米MiMo TTS，8种音色可选 | ✅ |
| 📢 **首页实时广播** | 最高优先级，打断当前播放，直接广播到指定区域 | ✅ |
| 🧩 **组合铃声** | 积木式组合：提示音 + TTS语音 + 正式铃声，顺序播放 | ✅ |
| 🔔 **提示音管理** | 上传/管理提示音文件，用于组合铃声前置音 | ✅ |
| 📅 **预约铃声** | 为特定课表任务临时替换铃声，到期自动生效 | ✅ |
| 🎨 **现代化UI** | 响应式设计，支持移动端访问 | ✅ |

### 🔮 后续规划

| 功能 | 说明 | 状态 |
|------|------|------|
| 👥 **多用户权限** | 角色级数据隔离（管理员/教师/查看者） | 🔄 计划中 |
| 📈 **数据统计** | 打铃历史统计、图表展示 | 🔄 计划中 |
| 🔔 **WebSocket推送** | 实时状态推送，无需轮询 | 🔄 计划中 |
| 🌐 **多语言支持** | 支持英文界面 | 🔄 计划中 |

---

## 🗣️ TTS语音合成

### 支持的TTS引擎

| 引擎 | 音色数 | 费用 | 说明 |
|------|--------|------|------|
| **Edge TTS（微软）** | 14个 | 🆓 免费 | 无需API Key，本地运行 |
| **小米MiMo TTS** | 8个 | 🆓 免费 | 需要API Key，高品质 |

### 🎙️ Edge TTS 音色列表

| 音色ID | 名称 | 性别 | 风格 |
|--------|------|------|------|
| zh-CN-XiaoxiaoNeural | 晓晓 | ♀ | 温暖亲切 ⭐推荐 |
| zh-CN-YunxiNeural | 云希 | ♂ | 阳光少年 |
| zh-CN-YunjianNeural | 云健 | ♂ | 沉稳大气 |
| zh-CN-XiaoyiNeural | 晓艺 | ♀ | 活泼可爱 |
| zh-CN-YunyangNeural | 云扬 | ♂ | 新闻播报 |
| zh-CN-XiaochenNeural | 晓辰 | ♀ | 专业成熟 |
| zh-CN-XiaohanNeural | 晓涵 | ♀ | 温柔体贴 |
| zh-CN-XiaomengNeural | 晓梦 | ♀ | 甜美可爱 |
| zh-CN-XiaomoNeural | 晓墨 | ♀ | 文艺清新 |
| zh-CN-XiaoqiuNeural | 晓秋 | ♀ | 成熟稳重 |
| zh-CN-XiaoruiNeural | 晓睿 | ♀ | 专业播报 |
| zh-CN-XiaoshuangNeural | 晓双 | ♀ | 童声 |
| zh-CN-XiaoyanNeural | 晓颜 | ♀ | 活力四射 |
| zh-CN-XiaozhenNeural | 晓甄 | ♀ | 端庄大方 |

### 🎙️ 小米MiMo TTS 音色列表

| 音色ID | 名称 | 性别 | 风格 |
|--------|------|------|------|
| 冰糖 | 冰糖 | ♀ | 清甜明亮，活泼可爱 |
| 茉莉 | 茉莉 | ♀ | 温柔细腻，清新淡雅 |
| Mia | Mia | ♀ | 优雅知性，温和亲切 |
| Chloe | Chloe | ♀ | 甜美温柔，情感丰富 ⭐推荐 |
| 苏打 | 苏打 | ♂ | 清爽自然，年轻活力 |
| Milo | Milo | ♂ | 温暖磁性，亲和力强 |
| 白桦 | 白桦 | ♂ | 沉稳厚重，专业权威 ⭐推荐广播 |
| Dean | Dean | ♂ | 浑厚低沉，刚毅有力 |

### 🔧 获取小米API Key

1. 访问 [小米MiMo控制台](https://platform.xiaomimimo.com/console/api-keys)
2. 创建账号并生成API Key
3. 在系统设置中输入API Key
4. 点击"检测"验证连接

---

## 📢 实时广播

### 功能特点

- ⚡ **最高优先级**：打断当前正在播放的铃声
- 🎯 **按区域广播**：可选择指定区域进行广播
- 📝 **常用预设**：提供5个常用广播内容快速选择
- 🔄 **自动恢复**：广播结束后自动恢复正常打铃

### 使用场景

- 📢 考试开始/结束通知
- 📢 紧急集合通知
- 📢 班主任通知
- 📢 临时通知

---

## 🧩 组合铃声

### 功能特点

- 🧱 **积木式组合**：像搭积木一样组合铃声
- 🔔 **提示音**：叮咚、警报等前置提示音
- 🗣️ **TTS语音**：自定义文字转语音
- 🎵 **正式铃声**：选择现有的铃声文件
- 👂 **试听功能**：组合完成后可预览效果

### 组合示例

```
考试结束铃 = 叮咚 + "考试时间到，请考生停止答题" + 结束铃
眼保健操 = 叮咚 + "眼保健操开始" + 眼保健操音乐
消防演练 = 警报 + "消防演练开始，请有序撤离" + 警报音
起床铃 = 叮咚 + "起床铃" + 进行曲
```

---

## 📅 预约铃声

### 功能特点

- 📅 **按任务预约**：为特定课表任务临时替换铃声
- ⏰ **时间范围**：设置生效的开始和结束日期
- 🔄 **自动生效**：到期自动使用预约铃声
- ↩️ **自动恢复**：过期自动恢复默认铃声
- 📝 **日志记录**：创建/删除预约都会记录日志

### 使用场景

- 📝 考试周使用特殊铃声
- 🎉 节假日使用节日铃声
- 🔧 设备维护期间暂停铃声
- 📢 临时活动使用特殊铃声

---

## 🏗️ 系统架构

### 📁 项目结构

```
钢城智慧铃声系统/
├── 🚀 run.py                 # 启动入口：Flask + APScheduler + 初始化
├── 🌐 app.py                 # Web API 路由（所有 /api/* 端点）
├── ⚙️ engine.py              # 核心引擎（打铃调度 + 音频播放 + NTP + 钉钉）
├── 💾 models.py              # SQLite 数据库（建表 + 迁移 + 日志/设置）
├── 🗣️ tts.py                 # TTS语音模块（Edge TTS + 小米MiMo TTS）
├── 📋 requirements.txt       # Python 依赖
├── 📂 templates/
│   ├── 📄 index.html         # 前端主界面（单页应用，约2100行）
│   └── 📄 login.html         # 登录界面
├── 📂 static/
│   ├── 📂 sounds/            # 铃声音频文件（.wav）
│   └── 📂 tts_cache/         # TTS缓存文件
├── 📂 data/                  # SQLite 数据库文件（自动创建）
├── 📂 logs/                  # 运行日志
└── 📂 backups/               # 数据库备份
```

### 🔄 模块依赖

```
run.py (主进程)
  ├── Flask app (app.py)
  │     ├── /api/status          → 系统状态
  │     ├── /api/schedules       → 课表管理
  │     ├── /api/bell/*          → 打铃控制
  │     ├── /api/tts/*           → TTS语音
  │     ├── /api/broadcast       → 实时广播
  │     ├── /api/overrides       → 预约铃声
  │     └── /api/logs            → 运行日志
  ├── APScheduler
  │     ├── bell_check_task      → 每秒检查打铃
  │     ├── ntp_sync_task        → 每日NTP校时
  │     └── tomorrow_alert       → 每日明日状态提醒
  └── 启动初始化
        ├── init_db()            → 数据库初始化
        └── engine初始化         → 加载配置
```

---

## 🗄️ 数据库设计

共 **12 张核心表**，SQLite 存储于 `data/school_bell.db`：

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `zones` | 区域 | id, name, enabled, volume, audio_device |
| `schedules` | 课表方案 | id, name, is_active |
| `schedule_tasks` | 打铃任务 | id, schedule_id, zone_id, time, bell_type |
| `bells` | 铃声文件 | id, name, filename, bell_type |
| `bell_bindings` | 区域-铃声绑定 | zone_id, bell_type, bell_id |
| `today_exceptions` | 今日例外 | date, zone_id, action |
| `tomorrow_overrides` | 明日覆盖 | date, zone_id, action |
| `bell_schedules` | 预约控制 | date, zone_id, action |
| `task_overrides` | 预约铃声 | task_id, start_date, end_date, bell_id |
| `custom_holidays` | 自定义节假日 | date, name, is_holiday |
| `settings` | 系统设置 | key, value |
| `logs` | 运行日志 | timestamp, level, category, message |

---

## 🔌 API文档

### 📍 基础路径

```
http://localhost:8787
```

### 🔐 认证

如果设置了密码，需要在请求头中添加：
```
X-Auth-Token: your_password
```

### 📊 系统状态

```http
GET /api/status
GET /api/health
```

### 📅 课表管理

```http
GET    /api/schedules          # 课表列表
POST   /api/schedules          # 创建课表
PUT    /api/schedules/{id}     # 更新课表
DELETE /api/schedules/{id}     # 删除课表
```

### ⏰ 任务管理

```http
POST   /api/tasks              # 添加任务
GET    /api/tasks/{id}         # 获取任务
PUT    /api/tasks/{id}         # 更新任务
DELETE /api/tasks/{id}         # 删除任务
```

### 🏠 区域管理

```http
GET    /api/zones              # 区域列表
POST   /api/zones              # 创建区域
PUT    /api/zones/{id}         # 更新区域
DELETE /api/zones/{id}         # 删除区域
```

### 🔔 打铃控制

```http
POST /api/bell/ring            # 手动打铃
POST /api/bell/pause           # 暂停
POST /api/bell/resume          # 恢复
POST /api/bell/stop            # 停止
```

### 📢 实时广播

```http
POST /api/broadcast            # 实时广播
POST /api/broadcast/stop       # 停止广播
```

### 🗣️ TTS语音

```http
GET  /api/tts/voices           # 音色列表
POST /api/tts/preview          # 试听
POST /api/tts/generate         # 生成TTS
GET  /api/tts/settings         # 获取设置
POST /api/tts/settings         # 保存设置
POST /api/tts/test_xiaomi      # 检测小米API
```

### 📅 预约铃声

```http
GET    /api/overrides          # 预约列表
POST   /api/overrides          # 创建预约
DELETE /api/overrides/{id}     # 删除预约
```

### 🎵 铃声管理

```http
GET    /api/bells              # 铃声列表
POST   /api/bells/upload       # 上传铃声
DELETE /api/bells/{id}         # 删除铃声
POST   /api/bell_bindings      # 更新绑定
GET    /api/prompts            # 提示音列表
```

### 📆 节假日

```http
GET  /api/holidays             # 节假日列表
POST /api/holidays/sync        # 同步节假日
POST /api/holidays/custom      # 添加自定义节假日
```

### ⚙️ 系统设置

```http
GET  /api/settings             # 获取设置
POST /api/settings             # 保存设置
POST /api/ntp/sync             # NTP校时
POST /api/dingtalk/test        # 测试钉钉
```

### 📊 其他

```http
GET /api/logs                  # 运行日志
GET /api/audio_devices         # 音频设备列表
GET /api/export                # 导出课表Excel
POST /api/import               # 导入课表Excel
```

---

## 🚀 快速开始

### 📋 环境要求

| 要求 | 版本 | 说明 |
|------|------|------|
| 🖥️ 操作系统 | Windows 10/11 | 依赖 WASAPI 音频 |
| 🐍 Python | 3.9+ | 推荐 3.11 |
| 🎵 VoiceMeeter | Banana | 免费，用于多声卡路由 |
| 💾 内存 | 2GB+ | 推荐 4GB |
| 💿 磁盘 | 100MB+ | 不含铃声文件 |

### 📥 安装步骤

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
   ```

4. **访问界面**
   ```
   浏览器打开 http://127.0.0.1:8787
   ```

### 📦 依赖列表

```
flask>=3.0              # Web框架
flask-apscheduler>=1.13 # 定时任务
numpy>=1.26             # 数值计算
sounddevice>=0.5        # 音频播放
soundfile>=0.12         # 音频文件读写
ntplib>=0.4             # NTP校时
openpyxl>=3.1           # Excel处理
pygame>=2.5             # 音频备用
edge-tts>=7.0           # Edge TTS语音合成
```

---

## ⚙️ 配置说明

### 🔧 首次配置流程

1. **设置密码**（可选）
   - 进入"系统设置" → "访问密码"
   - 设置管理员密码

2. **同步节假日**
   - 进入"节假日" → 点击"同步节假日"
   - 系统自动获取当年节假日数据

3. **创建课表**
   - 进入"排课管理" → 选择区域
   - 创建课表 → 添加打铃任务 → 设为默认

4. **配置区域**
   - 进入"区域控制" → 设置音量、音频设备
   - 绑定默认课表

5. **配置TTS**（可选）
   - 进入"系统设置" → "TTS语音设置"
   - 选择引擎和音色 → 试听 → 保存

6. **配置钉钉**（可选）
   - 进入"系统设置" → "钉钉机器人告警"
   - 输入Webhook地址 → 测试 → 保存

### 🔐 钉钉配置步骤

1. 打开钉钉群聊 → 右上角"..." → 群设置
2. 点击"智能群助手" → "添加机器人" → "自定义"
3. 安全设置选择"自定义关键词"，添加关键词"钢城智慧铃声"
4. 复制Webhook地址，粘贴到系统设置中
5. 点击"发送测试"验证配置

---

## 🎨 界面预览

### 📊 系统总览
- 今日/明日状态（按区域显示）
- 下次打铃倒计时
- 快捷操作按钮
- 实时广播区域

### 📅 排课管理
- 区域选择
- 课表管理
- 任务列表
- 批量操作

### 🔔 铃声管理
- 铃声库
- 组合铃声
- 提示音管理
- 区域绑定

### ⚙️ 系统设置
- TTS语音配置
- 钉钉告警配置
- NTP校时配置
- 访问密码设置

---

## 📅 版本历史

### 🆕 V5.0（2026-06-29）

**🎉 重大更新：新增TTS语音合成、实时广播、组合铃声、预约铃声**

#### ✨ 新增功能
- 🗣️ **TTS语音合成**
  - 支持 Edge TTS（微软）和 小米MiMo TTS
  - 14+种音色可选
  - 支持试听功能
  - 自动缓存生成结果

- 📢 **首页实时广播**
  - 最高优先级，打断当前播放
  - 按区域选择广播
  - 常用广播预设
  - 自动恢复播放

- 🧩 **组合铃声**
  - 积木式组合：提示音 + TTS + 铃声
  - 支持试听效果
  - 可命名保存
  - 复用现有铃声选择

- 🔔 **提示音管理**
  - 上传/删除提示音
  - 试听功能
  - 用于组合铃声前置音

- 📅 **预约铃声**
  - 为特定任务临时替换铃声
  - 支持时间范围设置
  - 自动生效/恢复
  - 日志记录

#### 🔧 优化改进
- 🎨 现代化UI设计
- 📱 响应式布局
- ⚡ 性能优化
- 🐛 Bug修复

#### 📝 文档更新
- 📖 完善README文档
- 📊 更新API文档
- 🎨 添加emoji美化

---

### V4.0（2026-06-17）

**🎉 初始版本发布**

#### ✨ 核心功能
- 🔔 多区域管理（A/B/C）
- 📅 课表管理
- ⏰ 智能打铃
- 🎵 多类型铃声
- 📆 节假日管理
- 🕐 NTP校时
- 📱 钉钉告警
- 📊 Excel导入导出
- 🔒 密码保护
- 💾 自动备份

---

## ❓ FAQ

### 🔧 安装配置

**Q: 如何安装VoiceMeeter？**
A: 访问 [VoiceMeeter官网](https://vb-audio.com/Voicemeeter/banana.htm) 下载安装，重启电脑后系统会自动配置。

**Q: NTP校时失败怎么办？**
A: 需要管理员权限运行程序，或手动配置Windows时间服务。

**Q: 如何添加新区域？**
A: 在"区域控制"页面点击"+ 新增区域"，输入区域ID和名称。

### 🗣️ TTS相关

**Q: 小米TTS如何获取API Key？**
A: 访问 https://platform.xiaomimimo.com/console/api-keys 注册并创建API Key。

**Q: TTS生成失败怎么办？**
A: 检查网络连接，确认API Key正确，尝试更换音色。

**Q: 如何选择适合广播的音色？**
A: 推荐使用"白桦"（男声沉稳）或"Chloe"（女声温柔）。

### 🔔 铃声相关

**Q: 组合铃声是什么？**
A: 组合铃声可以将提示音、TTS语音、正式铃声按顺序播放，实现"叮咚 + 语音提示 + 铃声"的效果。

**Q: 预约铃声和今日控制有什么区别？**
A: 今日控制当天生效，预约铃声可提前任意天数设置，且支持任务级替换。

**Q: 如何备份数据？**
A: 系统每日凌晨2:30自动备份数据库到`backups/`目录，保留7天。

### 📱 其他

**Q: 支持移动端访问吗？**
A: 支持，系统采用响应式设计，可在手机浏览器访问。

**Q: 如何查看运行日志？**
A: 在"运行日志"页面可查看所有操作记录，支持按类别筛选。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 📝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## 🙏 致谢

- [Flask](https://flask.palletsprojects.com/) - Web框架
- [APScheduler](https://apscheduler.readthedocs.io/) - 定时任务
- [sounddevice](https://python-sounddevice.readthedocs.io/) - 音频播放
- [Edge TTS](https://github.com/rany2/edge-tts) - 微软TTS
- [小米MiMo](https://mimo.mi.com/) - 小米TTS

---

<p align="center">
  <sub>🎓 Made with ❤️ for schools · 钢城智慧铃声系统</sub>
</p>
