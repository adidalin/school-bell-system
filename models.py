"""
校园智能广播定时系统 V4.0 - 数据库模型
SQLite数据库，区域独立课表、今日例外、铃声管理、节假日、设置
"""

import sqlite3
import json
import os
import logging
from datetime import datetime, date, timedelta
from pathlib import Path

logger = logging.getLogger("SchoolBell")

DB_PATH = "data/school_bell.db"


def get_db():
    """获取数据库连接"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _migrate_db():
    """数据库迁移：添加新列和新表"""
    conn = get_db()
    c = conn.cursor()

    # 1. today_exceptions增加schedule_id列
    cols = [row[1] for row in c.execute("PRAGMA table_info(today_exceptions)").fetchall()]
    if "schedule_id" not in cols:
        c.execute("ALTER TABLE today_exceptions ADD COLUMN schedule_id INTEGER DEFAULT 0")
        logger.info("数据库迁移: today_exceptions添加schedule_id列")

    # 2. zones表增加schedule_id列（区域绑定默认课表）
    zone_cols = [row[1] for row in c.execute("PRAGMA table_info(zones)").fetchall()]
    if "schedule_id" not in zone_cols:
        c.execute("ALTER TABLE zones ADD COLUMN schedule_id INTEGER DEFAULT 0")
        logger.info("数据库迁移: zones添加schedule_id列")

    # 3. 创建明日状态覆盖表
    c.execute("""
        CREATE TABLE IF NOT EXISTS tomorrow_overrides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            zone_id TEXT NOT NULL,
            action TEXT NOT NULL,
            schedule_id INTEGER DEFAULT 0,
            reason TEXT DEFAULT '',
            created_at TEXT DEFAULT '',
            UNIQUE(date, zone_id)
        )
    """)

    # 4. today_exceptions修改UNIQUE约束：改为(date, zone_id)
    # 4. schedule_tasks表增加bell_id字段（关联具体铃声文件）
    task_cols = [row[1] for row in c.execute("PRAGMA table_info(schedule_tasks)").fetchall()]
    if "bell_id" not in task_cols:
        c.execute("ALTER TABLE schedule_tasks ADD COLUMN bell_id INTEGER DEFAULT 0")
        logger.info("数据库迁移: schedule_tasks添加bell_id列")

    # 5. schedules表增加created_by字段（记录创建者）
    sched_cols = [row[1] for row in c.execute("PRAGMA table_info(schedules)").fetchall()]
    if "created_by" not in sched_cols:
        c.execute("ALTER TABLE schedules ADD COLUMN created_by TEXT DEFAULT ''")
        logger.info("数据库迁移: schedules添加created_by列")

    # 6. today_exceptions修改UNIQUE约束：改为(date, zone_id)
    # SQLite不支持ALTER约束，通过重建表实现
    te_cols = [row[1] for row in c.execute("PRAGMA table_info(today_exceptions)").fetchall()]
    if "" not in [row[3] for row in c.execute("PRAGMA table_info(today_exceptions)").fetchall()
                   if row[1] == "zone_id"]:
        # zone_id没有NOT NULL约束，需要重建表以支持按区域的UNIQUE
        pass  # 保持现有表结构，通过代码逻辑处理

    # 6. 创建预约控制表（未来任意日期按区域开关铃声）
    c.execute("""
        CREATE TABLE IF NOT EXISTS bell_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            zone_id TEXT NOT NULL,
            action TEXT NOT NULL DEFAULT 'force_no_ring',
            schedule_id INTEGER DEFAULT 0,
            reason TEXT DEFAULT '',
            remind_enabled INTEGER DEFAULT 1,
            remind_at TEXT DEFAULT '20:00',
            reminded INTEGER DEFAULT 0,
            created_at TEXT DEFAULT '',
            UNIQUE(date, zone_id)
        )
    """)

    conn.commit()
    conn.close()


def init_db():
    """初始化数据库表"""
    conn = get_db()
    c = conn.cursor()

    # 区域表
    c.execute("""
        CREATE TABLE IF NOT EXISTS zones (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL DEFAULT '',
            enabled INTEGER DEFAULT 1,
            audio_device TEXT DEFAULT '',
            volume REAL DEFAULT 1.0,
            sort_order INTEGER DEFAULT 0
        )
    """)

    # 课表方案表
    c.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            is_active INTEGER DEFAULT 0
        )
    """)

    # 课表任务表（每个区域独立）
    c.execute("""
        CREATE TABLE IF NOT EXISTS schedule_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            schedule_id INTEGER NOT NULL,
            zone_id TEXT NOT NULL,
            time TEXT NOT NULL,
            bell_type TEXT DEFAULT 'class_start',
            task_name TEXT DEFAULT '',
            days TEXT DEFAULT '1,2,3,4,5',
            one_time_date TEXT DEFAULT '',
            FOREIGN KEY (schedule_id) REFERENCES schedules(id) ON DELETE CASCADE,
            FOREIGN KEY (zone_id) REFERENCES zones(id)
        )
    """)

    # 铃声文件表
    c.execute("""
        CREATE TABLE IF NOT EXISTS bells (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            filename TEXT NOT NULL,
            bell_type TEXT DEFAULT 'custom',
            duration REAL DEFAULT 0,
            uploaded_at TEXT DEFAULT ''
        )
    """)

    # 铃声类型绑定表（每个区域可绑定不同铃声）
    c.execute("""
        CREATE TABLE IF NOT EXISTS bell_bindings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            zone_id TEXT NOT NULL,
            bell_type TEXT NOT NULL,
            bell_id INTEGER NOT NULL,
            FOREIGN KEY (zone_id) REFERENCES zones(id),
            FOREIGN KEY (bell_id) REFERENCES bells(id)
        )
    """)

    # 今日例外表（按区域独立控制）
    c.execute("""
        CREATE TABLE IF NOT EXISTS today_exceptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            zone_id TEXT NOT NULL DEFAULT '',
            action TEXT NOT NULL,
            reason TEXT DEFAULT '',
            created_at TEXT DEFAULT '',
            schedule_id INTEGER DEFAULT 0,
            UNIQUE(date, zone_id)
        )
    """)

    # 自定义节假日表
    c.execute("""
        CREATE TABLE IF NOT EXISTS custom_holidays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            is_holiday INTEGER DEFAULT 1
        )
    """)

    # 系统设置表
    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT DEFAULT ''
        )
    """)

    # 运行日志表
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT DEFAULT 'INFO',
            category TEXT DEFAULT 'system',
            message TEXT NOT NULL,
            detail TEXT DEFAULT ''
        )
    """)

    # 预约控制表（未来任意日期按区域开关铃声）
    c.execute("""
        CREATE TABLE IF NOT EXISTS bell_schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            zone_id TEXT NOT NULL,
            action TEXT NOT NULL DEFAULT 'force_no_ring',
            schedule_id INTEGER DEFAULT 0,
            reason TEXT DEFAULT '',
            remind_enabled INTEGER DEFAULT 1,
            remind_at TEXT DEFAULT '20:00',
            reminded INTEGER DEFAULT 0,
            created_at TEXT DEFAULT '',
            UNIQUE(date, zone_id)
        )
    """)

    # 预约铃声表（任务级临时换铃）
    c.execute("""
        CREATE TABLE IF NOT EXISTS task_overrides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            bell_id INTEGER NOT NULL,
            created_at TEXT DEFAULT '',
            UNIQUE(task_id, start_date)
        )
    """)

    # 初始化默认数据
    _init_default_data(c)

    conn.commit()
    conn.close()

    # 执行数据库迁移
    _migrate_db()

    logger.info("数据库初始化完成")


def _init_default_data(c):
    """初始化默认区域、课表、铃声绑定等"""
    # 默认3个区域
    zones = c.execute("SELECT COUNT(*) FROM zones").fetchone()[0]
    if zones == 0:
        c.executemany("INSERT INTO zones (id, name, enabled, volume, sort_order) VALUES (?,?,?,?,?)", [
            ("A", "教学楼", 1, 0.8, 1),
            ("B", "操场", 1, 1.0, 2),
            ("C", "宿舍楼", 1, 0.6, 3),
        ])
        logger.info("已创建默认3个区域")

    # 默认课表
    sched = c.execute("SELECT COUNT(*) FROM schedules").fetchone()[0]
    if sched == 0:
        # 平日课表
        c.execute("INSERT INTO schedules (name, is_active) VALUES ('平日课表', 1)")
        sid = c.execute("SELECT last_insert_rowid()").fetchone()[0]

        # 教学楼平日课表
        default_tasks_a = [
            (sid, "A", "07:50", "prepare", "预备铃", "1,2,3,4,5", ""),
            (sid, "A", "08:00", "class_start", "第一节课上课", "1,2,3,4,5", ""),
            (sid, "A", "08:45", "class_end", "第一节课下课", "1,2,3,4,5", ""),
            (sid, "A", "08:55", "class_start", "第二节课上课", "1,2,3,4,5", ""),
            (sid, "A", "09:40", "class_end", "第二节课下课", "1,2,3,4,5", ""),
            (sid, "A", "09:50", "exercise", "课间操", "1,2,3,4,5", ""),
            (sid, "A", "10:20", "class_start", "第三节课上课", "1,2,3,4,5", ""),
            (sid, "A", "11:05", "class_end", "第三节课下课", "1,2,3,4,5", ""),
            (sid, "A", "11:15", "class_start", "第四节课上课", "1,2,3,4,5", ""),
            (sid, "A", "12:00", "lunch", "午餐铃", "1,2,3,4,5", ""),
            (sid, "A", "14:00", "class_start", "第五节课上课", "1,2,3,4,5", ""),
            (sid, "A", "14:45", "class_end", "第五节课下课", "1,2,3,4,5", ""),
            (sid, "A", "14:55", "class_start", "第六节课上课", "1,2,3,4,5", ""),
            (sid, "A", "15:40", "class_end", "第六节课下课", "1,2,3,4,5", ""),
            (sid, "A", "15:50", "class_start", "第七节课上课", "1,2,3,4,5", ""),
            (sid, "A", "16:35", "class_end", "第七节课下课", "1,2,3,4,5", ""),
            (sid, "A", "16:45", "class_start", "第八节课上课", "1,2,3,4,5", ""),
            (sid, "A", "17:30", "school_end", "放学铃", "1,2,3,4,5", ""),
        ]
        c.executemany(
            "INSERT INTO schedule_tasks (schedule_id, zone_id, time, bell_type, task_name, days, one_time_date) VALUES (?,?,?,?,?,?,?)",
            default_tasks_a
        )

        # 宿舍楼平日课表
        default_tasks_c = [
            (sid, "C", "06:30", "prepare", "起床铃", "1,2,3,4,5", ""),
            (sid, "C", "07:00", "class_start", "出宿舍", "1,2,3,4,5", ""),
            (sid, "C", "12:00", "lunch", "午餐铃", "1,2,3,4,5", ""),
            (sid, "C", "13:00", "class_end", "午休结束", "1,2,3,4,5", ""),
            (sid, "C", "22:00", "school_end", "熄灯铃", "1,2,3,4,5", ""),
        ]
        c.executemany(
            "INSERT INTO schedule_tasks (schedule_id, zone_id, time, bell_type, task_name, days, one_time_date) VALUES (?,?,?,?,?,?,?)",
            default_tasks_c
        )

        # 考试课表
        c.execute("INSERT INTO schedules (name, is_active) VALUES ('考试课表', 0)")
        eid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
        exam_tasks = [
            (eid, "A", "07:50", "prepare", "预备铃", "1,2,3,4,5", ""),
            (eid, "A", "08:00", "class_start", "语文考试开始", "1,2,3,4,5", ""),
            (eid, "A", "10:00", "class_end", "语文考试结束", "1,2,3,4,5", ""),
            (eid, "A", "10:20", "class_start", "数学考试开始", "1,2,3,4,5", ""),
            (eid, "A", "12:00", "lunch", "午餐铃", "1,2,3,4,5", ""),
            (eid, "A", "14:00", "class_start", "英语考试开始", "1,2,3,4,5", ""),
            (eid, "A", "16:00", "school_end", "考试结束", "1,2,3,4,5", ""),
        ]
        c.executemany(
            "INSERT INTO schedule_tasks (schedule_id, zone_id, time, bell_type, task_name, days, one_time_date) VALUES (?,?,?,?,?,?,?)",
            exam_tasks
        )

        logger.info("已创建默认课表（平日+考试）")

    # 默认设置
    sett = c.execute("SELECT COUNT(*) FROM settings").fetchone()[0]
    if sett == 0:
        default_settings = [
            ("ntp_enabled", "1"),
            ("ntp_server", "ntp.aliyun.com"),
            ("ntp_daily_time", "06:00"),
            ("ntp_last_sync", ""),
            ("dingtalk_enabled", "0"),
            ("dingtalk_webhook", ""),
            ("dingtalk_keyword", "校园广播"),
            ("holiday_api_enabled", "1"),
            ("holiday_last_fetch", ""),
            ("holiday_data", "{}"),
            ("password", ""),
            ("port", "8787"),
            ("auto_start", "0"),
        ]
        c.executemany("INSERT INTO settings (key, value) VALUES (?,?)", default_settings)
        logger.info("已创建默认设置")


def add_log(level="INFO", category="system", message="", detail=""):
    """添加运行日志"""
    conn = get_db()
    conn.execute(
        "INSERT INTO logs (timestamp, level, category, message, detail) VALUES (?,?,?,?,?)",
        (datetime.now().isoformat(), level, category, message, detail)
    )
    conn.commit()
    conn.close()


def get_setting(key, default=""):
    """获取设置值"""
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    """设置值"""
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?,?)", (key, str(value)))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    init_db()
    print("数据库初始化完成")

    # 验证
    conn = get_db()
    zones = conn.execute("SELECT * FROM zones").fetchall()
    print(f"区域: {len(zones)}个")
    for z in zones:
        print(f"  {z['id']}: {z['name']}")

    schedules = conn.execute("SELECT * FROM schedules").fetchall()
    print(f"课表: {len(schedules)}套")
    for s in schedules:
        tasks = conn.execute("SELECT COUNT(*) as cnt FROM schedule_tasks WHERE schedule_id=?", (s['id'],)).fetchone()
        active = "✅激活" if s['is_active'] else ""
        print(f"  {s['name']}: {tasks['cnt']}条任务 {active}")

    settings = conn.execute("SELECT * FROM settings").fetchall()
    print(f"设置: {len(settings)}项")

    conn.close()
