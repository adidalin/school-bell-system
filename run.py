"""
校园智能广播系统 V4.0 - 启动脚本
启动Flask + APScheduler，含每日NTP校时、定期打铃调度
"""

import os
import sys
import logging
from datetime import datetime, date

# 确保当前目录在sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask_apscheduler import APScheduler

from models import init_db, get_db, get_setting, add_log, set_setting
from engine import engine
from app import app as flask_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/school_bell.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger("SchoolBell")

scheduler = APScheduler()
scheduler.init_app(flask_app)
scheduler.start()


# ===== APScheduler 定时任务 =====

@scheduler.task("interval", id="bell_check", seconds=1)
def bell_check_task():
    """每秒检查打铃"""
    try:
        engine.check_and_ring()
    except Exception as e:
        logger.error(f"打铃检查异常: {e}")


@scheduler.task("cron", id="ntp_daily", hour=6, minute=0)
def ntp_daily_task():
    """每天早上6:00自动NTP校时"""
    enabled = get_setting("ntp_enabled", "1")
    if enabled == "1":
        server = get_setting("ntp_server", "ntp.aliyun.com")
        logger.info("每日自动NTP校时...")
        success, result = engine.ntp.sync(server)
        if success:
            set_setting("ntp_last_sync", date.today().isoformat())
            add_log("INFO", "ntp", f"每日校时成功，偏差{result:.3f}秒")
        else:
            add_log("ERROR", "ntp", f"每日校时失败: {result}")


@scheduler.task("interval", id="ntp_sync_interval", minutes=60)
def ntp_interval_task():
    """每小时检查一次NTP同步（如果设置了）"""
    enabled = get_setting("ntp_enabled", "1")
    if enabled == "1":
        server = get_setting("ntp_server", "ntp.aliyun.com")
        engine.ntp.sync(server)


# ===== 运维任务 =====

@scheduler.task("cron", id="log_cleanup", hour=3, minute=0)
def log_cleanup_task():
    """每日凌晨3:00清理旧日志（保留30天）和旧备份（保留7天）"""
    _cleanup_old_logs()
    _cleanup_old_backups()


@scheduler.task("cron", id="db_backup", hour=2, minute=30)
def db_backup_task():
    """每日凌晨2:30自动备份数据库"""
    _backup_database()


def _cleanup_old_logs():
    """删除30天前的日志文件"""
    import glob
    import time as _time
    logs_dir = "logs"
    cutoff = _time.time() - 30 * 86400
    count = 0
    for pattern in ["*.log", "*.log.*"]:
        for f in glob.glob(os.path.join(logs_dir, pattern)):
            try:
                if os.path.getmtime(f) < cutoff:
                    os.remove(f)
                    count += 1
            except OSError:
                pass
    if count:
        logger.info(f"日志清理: 已删除 {count} 个旧日志文件")


def _backup_database():
    """备份SQLite数据库到 backups/ 目录"""
    import shutil
    from datetime import date as _date
    from models import DB_PATH
    src = DB_PATH
    if not os.path.exists(src):
        logger.warning("数据库备份: 数据库文件不存在，跳过")
        return
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    today = _date.today().isoformat()
    dst = os.path.join(backup_dir, f"school_bell_{today}.db")
    if os.path.exists(dst):
        return  # 今天已备份
    try:
        shutil.copy2(src, dst)
        size = os.path.getsize(dst)
        logger.info(f"数据库备份完成: {dst} ({size/1024:.0f}KB)")
        add_log("INFO", "system", f"数据库自动备份: {today}")
    except Exception as e:
        logger.error(f"数据库备份失败: {e}")


def _cleanup_old_backups():
    """删除7天前的数据库备份"""
    import glob
    import time as _time
    backup_dir = "backups"
    if not os.path.isdir(backup_dir):
        return
    cutoff = _time.time() - 7 * 86400
    count = 0
    for f in glob.glob(os.path.join(backup_dir, "*.db")):
        try:
            if os.path.getmtime(f) < cutoff:
                os.remove(f)
                count += 1
        except OSError:
            pass
    if count:
        logger.info(f"备份清理: 已删除 {count} 个旧备份")


@scheduler.task("cron", id="holiday_fetch", day=1, hour=2)
def holiday_fetch_task():
    """每月1号凌晨2点获取新一年节假日数据"""
    year = date.today().year
    logger.info(f"每月定时获取{year}年节假日数据...")
    engine.holiday.fetch_year(year)


@scheduler.task("interval", id="status_log", minutes=10)
def status_log_task():
    """每10分钟记录一次系统状态"""
    next_bells = engine.get_next_bell()
    status = "暂停" if engine.player.is_global_paused() else "运行中"
    info = f"系统状态: {status}"
    if next_bells:
        parts = []
        for nb in next_bells[:3]:
            parts.append(f"{nb['zone_name']} {nb['time']} {nb['name']}")
        info += "，下次打铃: " + " | ".join(parts)
    add_log("INFO", "system", info)


@scheduler.task("cron", id="tomorrow_alert", hour=8, minute=0)
def tomorrow_alert_task():
    """每天早上8:00检查明日状态，如非常规则发钉钉提醒"""
    try:
        engine.check_tomorrow_and_alert()
    except Exception as e:
        logger.error(f"明日状态检查异常: {e}")


@scheduler.task("cron", id="bell_schedule_migrate", hour=1, minute=0)
def bell_schedule_migrate_task():
    """每天凌晨1:00将今天的预约控制迁移到today_exceptions"""
    try:
        logger.info("执行预约控制迁移...")
        engine.process_bell_schedules("migrate")
    except Exception as e:
        logger.error(f"预约控制迁移异常: {e}")


# ===== 初始化 =====
def init_system():
    """系统初始化"""
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("static/sounds", exist_ok=True)

    # 初始化数据库
    init_db()

    # 将今日的tomorrow_overrides迁移为today_exceptions
    _migrate_tomorrow_to_today()

    # 迁移今天的bell_schedules到today_exceptions
    engine.process_bell_schedules("migrate")

    # 加载设置到引擎
    dingtalk_webhook = get_setting("dingtalk_webhook", "")
    dingtalk_enabled = get_setting("dingtalk_enabled", "0") == "1"
    engine.dingtalk.configure(dingtalk_webhook, dingtalk_enabled)

    # 获取本学期节假日数据
    year = date.today().year
    engine.holiday.fetch_year(year)

    # 启动NTP首次校时
    ntp_enabled = get_setting("ntp_enabled", "1")
    if ntp_enabled == "1":
        server = get_setting("ntp_server", "ntp.aliyun.com")
        logger.info("启动时NTP校时...")
        success, result = engine.ntp.sync(server)
        if success:
            set_setting("ntp_last_sync", datetime.now().isoformat())

    add_log("INFO", "system", "钢城智慧铃声系统V5.0启动完成")
    logger.info("=" * 50)
    logger.info("钢城智慧铃声系统 V5.0 启动成功!")
    logger.info(f"访问地址: http://0.0.0.0:{get_setting('port', '8787')}")
    logger.info("=" * 50)


def _migrate_tomorrow_to_today():
    """将昨天设置的明日覆盖迁移为今日例外"""
    from datetime import date as date_cls
    conn = get_db()
    today_str = date_cls.today().isoformat()

    # 查找今天日期的tomorrow_overrides
    overrides = conn.execute(
        "SELECT * FROM tomorrow_overrides WHERE date=?", (today_str,)
    ).fetchall()

    for ov in overrides:
        # 检查是否已有对应的today_exception
        existing = conn.execute(
            "SELECT * FROM today_exceptions WHERE date=? AND zone_id=?",
            (today_str, ov["zone_id"])
        ).fetchone()
        if not existing:
            conn.execute(
                "INSERT INTO today_exceptions (date, zone_id, action, reason, created_at, schedule_id) VALUES (?,?,?,?,?,?)",
                (today_str, ov["zone_id"], ov["action"],
                 ov["reason"] or "", ov["created_at"] or "",
                 ov["schedule_id"] if "schedule_id" in ov.keys() else 0)
            )
            logger.info(f"迁移明日覆盖: {ov['zone_id']} {ov['action']}")

    # 清除已过期的tomorrow_overrides（3天前）
    conn.execute("DELETE FROM tomorrow_overrides WHERE date < date('now', '-3 days')")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_system()
    port = int(get_setting("port", "8787"))
    flask_app.run(host="0.0.0.0", port=port, debug=False)
