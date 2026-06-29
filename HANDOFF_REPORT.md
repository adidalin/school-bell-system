# 项目当前阶段交接报告

> 生成时间：2026-06-29 | 版本：V4.0/V5.0

---

## 一、当前功能实现清单（Status）

### ✅ 已完整实现的功能

- **系统总览仪表盘**：实时时间、NTP状态、系统运行状态、下次打铃倒计时
- **多区域管理**：A/B/C（教学楼/操场/宿舍楼）+ 自定义区域，每个区域独立控制
- **课表管理**：多套课表（平日/考试），支持新建、激活、删除
- **排课管理V2**：按区域优先视角管理课表任务，支持全区域批量添加
- **打铃任务调度**：每秒检查，精确到分钟触发，支持周几重复和一次性日期
- **多类型铃声**：上课铃/下课铃/预备铃/课间操/午餐铃/放学铃/紧急铃/自定义
- **铃声文件管理**：上传/删除铃声文件（MP3/WAV/OGG/M4A/AAC/FLAC/WMA），MP3自动转WAV
- **区域铃声绑定**：每个区域可绑定不同铃声文件，矩阵式配置
- **今日/明日控制**：按区域独立设置今日打铃/不打铃/恢复自动
- **预约控制**：预设未来任意日期的铃声开关，自动迁移生效
- **节假日管理**：自动获取中国法定节假日，支持自定义节假日/调休
- **NTP网络校时**：每日自动校准，支持直接设置系统时钟或配置Windows时间服务
- **钉钉机器人告警**：打铃异常告警、明日状态提醒、预约提醒（30分钟冷却）
- **Excel导入导出**：课表可导入/导出Excel，支持模板下载
- **运行日志**：分类记录打铃/手动/例外/系统/设置等日志
- **数据库自动备份**：每日凌晨2:30备份，保留7天
- **日志自动清理**：保留30天运行日志
- **密码保护**：可选的访问密码（MD5存储）
- **VoiceMeeter集成**：自动启动/配置VoiceMeeter Banana音频路由
- **音频设备管理**：支持多声卡独立输出（WDM-KS直连）
- **手动打铃控制**：全局暂停/恢复/停止，按区域暂停/恢复/测试打铃

### ⬜ 待扩展的功能（已搭建架子）

- **多用户权限**：目前仅单密码认证，无角色/权限区分
- **打铃历史统计**：有日志但无统计图表
- **Websocket实时推送**：目前前端轮询刷新（30秒），未实现实时推送
- **预约铃声**：独立页面，绑定task的临时换铃（TODO.md中有详细设计）
- **TTS前置语音**：打铃时先播放TTS语音再播放铃声（TODO.md中有详细设计）

---

## 二、当前项目结构（Project Structure）

```
钢城智慧铃声系统/
├── run.py                 # 启动入口：Flask + APScheduler + 初始化（328行）
├── app.py                 # Web API路由（1191行）
├── engine.py              # 核心引擎：NTP/音频播放/钉钉/节假日/调度（1154行）
├── models.py              # SQLite数据库：建表+迁移+日志/设置读写（382行）
├── requirements.txt       # Python依赖
├── templates/
│   ├── index.html         # 主界面SPA（1339行，含全部前端逻辑）
│   └── login.html         # 登录页
├── static/sounds/         # 铃声音频文件
├── data/
│   └── school_bell.db     # SQLite数据库（运行时生成）
├── logs/                  # 运行日志
├── backups/               # 数据库备份
└── scripts/               # 启动脚本（bat/vbs/ps1）
```

---

## 三、核心代码结构概要

### models.py（数据库层）
- `get_db()` → SQLite连接（WAL模式，Row factory）
- `init_db()` → 创建9张表（zones, schedules, schedule_tasks, bells, bell_bindings, today_exceptions, tomorrow_overrides, bell_schedules, custom_holidays, settings, logs）
- `_migrate_db()` → 自动迁移（加列、加表）
- `get_setting()/set_setting()` → KV设置读写
- `add_log()` → 写日志

### engine.py（核心引擎）
```
NTPSync
  └── sync() → 3次测量取中位数，偏差>0.2s时SetSystemTime或配置w32time

AudioPlayer
  ├── _get_or_create_stream() → 每设备一个OutputStream
  ├── play(zone_id, filepath, volume) → 读取音频→重采样→播放
  └── _device_id(zone_id) → 查找WASAPI/WDM-KS设备

HolidayChecker
  ├── fetch_year() → 从timor.tech获取节假日
  └── should_bell_today() → 判断今天是否打铃（含调休）

DingTalkNotifier
  └── send() → 钉钉Webhook推送（30分钟冷却）

BellEngine（主引擎）
  ├── check_and_ring() → 每秒调用，遍历区域→查课表→匹配时间→播放铃声
  ├── _get_zone_schedule() → 确定区域使用的课表（优先级：today_exception > zone.schedule_id > 全局激活）
  ├── manual_bell() → 手动打铃
  ├── get_next_bell() → 获取下次打铃信息
  ├── check_tomorrow_and_alert() → 每日8:00检查明日状态，发钉钉提醒
  └── process_bell_schedules() → 预约控制迁移
```

### app.py（API路由）
- `/api/status` → 系统总览（区域状态、下次打铃、NTP）
- `/api/schedules` → 课表CRUD
- `/api/tasks` → 任务CRUD
- `/api/zones` → 区域CRUD
- `/api/bells` → 铃声上传/删除
- `/api/bell_bindings` → 区域-铃声绑定
- `/api/bell/ring|pause|resume|stop` → 打铃控制
- `/api/today_control` → 今日控制（ring/no_ring/auto）
- `/api/tomorrow_control` → 明日控制
- `/api/bell_schedules` → 预约控制CRUD
- `/api/holidays` → 节假日管理
- `/api/settings` → 系统设置
- `/api/ntp/sync` → NTP校时
- `/api/export|import` → Excel导入导出

### run.py（启动入口）
- APScheduler定时任务：
  - `bell_check_task` → 每秒调用engine.check_and_ring()
  - `ntp_daily_task` → 每日6:00 NTP校时
  - `tomorrow_alert_task` → 每日8:00明日状态检查
  - `bell_schedule_migrate_task` → 每日1:00预约迁移
  - `status_log_task` → 每10分钟记录状态
  - `db_backup_task` → 每日2:30数据库备份
  - `log_cleanup_task` → 每日3:00日志清理

### index.html（前端SPA）
- 单文件SPA，原生JS，无框架依赖
- 9个页面：总览/课表/排课V2/区域/铃声/节假日/预约/设置/日志
- 全局变量：`ZN`(区域名映射)、`ZONES`(区域列表)、`BELLS`(铃声列表)
- API调用：`api(path, method, data)` 封装fetch
- 定时刷新：每30秒刷新区域状态

---

## 四、技术实现特点

### 数据存储
- **SQLite**（data/school_bell.db）：所有业务数据持久化存储
- WAL模式：崩溃安全，写入先写WAL再写DB
- KV设置表：settings表存储所有配置（ntp_server, dingtalk_webhook, password等）
- 数据备份：每日自动备份到backups/目录

### 页面交互
- **前端轮询**：每30秒调用`/api/status`刷新状态
- **SPA路由**：通过CSS类切换`.page.active`实现页面切换
- **弹窗编辑**：任务/区域/节假日通过modal弹窗编辑
- **Toast提示**：操作成功/失败通过右上角Toast提示

### 定时调度
- **APScheduler**：Flask集成，后台线程执行
- **打铃检查**：每秒执行，只在每分钟第0秒触发
- **NTP校时**：3次测量取中位数消抖
- **预约迁移**：每日凌晨自动将预约迁移到今日例外

### 音频播放
- **sounddevice**：PortAudio绑定，WASAPI共享模式多路混音
- **每设备独立OutputStream**：支持多声卡并行输出
- **VoiceMeeter**：虚拟音频路由，VAIO→A1(音箱), AUX→A2(耳机)
- **自动重采样**：所有音频统一重采样到48kHz

### 告警系统
- **钉钉Webhook**：Markdown格式推送
- **30分钟冷却**：同类告警不重复
- **三类告警**：明日异常预提醒(8:00) + 实时异常 + 关键操作

---

## 五、数据库表结构（9张核心表）

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| zones | 区域 | id(PK), name, enabled, volume, audio_device, schedule_id |
| schedules | 课表方案 | id(PK), name, is_active |
| schedule_tasks | 打铃任务 | id(PK), schedule_id(FK), zone_id, time, bell_type, days, bell_id |
| bells | 铃声库 | id(PK), name, filename, bell_type |
| bell_bindings | 区域-铃声绑定 | zone_id, bell_type, bell_id |
| today_exceptions | 今日例外 | date, zone_id, action(force_ring/force_no_ring), schedule_id |
| tomorrow_overrides | 明日覆盖 | date, zone_id, action, schedule_id |
| bell_schedules | 预约控制 | date, zone_id, action, schedule_id, remind_enabled, reminded |
| custom_holidays | 自定义节假日 | date, name, is_holiday |
| settings | 系统设置(KV) | key(PK), value |
| logs | 运行日志 | timestamp, level, category, message |

---

## 六、快速启动

```bash
# 安装依赖
pip install -r requirements.txt

# 启动系统
python run.py

# 访问界面
# 浏览器打开 http://127.0.0.1:8787
```

---

## 七、后续开发指引

详见 `TODO.md`，主要待开发项：
1. **预约铃声**（独立页面，~180行）→ P0优先级
2. **TTS前置语音**（~70行）→ P1优先级
3. **PocketBase权限系统**（~300行）→ P2优先级

---

*本报告由opencode自动生成，供AI工具接手使用*
