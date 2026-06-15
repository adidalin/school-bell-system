"""
校园智能广播定时系统 V4.0 - 核心引擎
Flask + APScheduler 定时调度 + NTP校时 + 音频播放 + 异常检测
"""

import os
import sys
import json
import time
import logging
import threading
import urllib.request
from datetime import datetime, date, timedelta
from pathlib import Path

logger = logging.getLogger("SchoolBell")

# ====== NTP校时模块 ======
class NTPSync:
    """NTP网络校时"""

    def __init__(self):
        self.last_sync = None
        self.offset = 0.0

    def sync(self, server="ntp.aliyun.com"):
        """执行NTP校时。先尝试直接校准（需管理员），否则配置Windows时间服务自动同步"""
        try:
            import ntplib

            # 取3次测量取中位数，减少网络抖动
            client = ntplib.NTPClient()
            offsets = []
            for _ in range(3):
                try:
                    resp = client.request(server, timeout=3)
                    offsets.append(resp.offset)
                except Exception:
                    pass

            if not offsets:
                raise Exception("所有NTP请求均超时")

            offsets.sort()
            offset = offsets[len(offsets) // 2]
            self.offset = offset
            self.last_sync = datetime.now().isoformat()

            if abs(offset) > 0.2:
                corrected = self._set_system_time_direct(offset)
                if corrected:
                    try:
                        resp2 = client.request(server, timeout=3)
                        logger.info(f"NTP校准完成: {offset:+.3f}s → {resp2.offset:+.3f}s")
                        self.offset = resp2.offset
                    except Exception:
                        logger.info(f"NTP校准完成: {offset:+.3f}s")
                else:
                    # 直接校准失败（通常因无管理员权限），尝试配置Windows时间服务
                    configured = self._configure_w32time(server)
                    if configured:
                        logger.warning(
                            f"NTP偏差 {offset:+.3f}s —— 已配置Windows时间服务自动校准，"
                            f"下次系统时间同步后生效"
                        )
                    else:
                        logger.warning(
                            f"NTP偏差 {offset:+.3f}s —— 校准失败（需要管理员权限），"
                            f"建议以管理员身份运行程序"
                        )
            else:
                logger.info(f"NTP: {offset:+.3f}s")

            return True, offset
        except Exception as e:
            logger.error(f"NTP校时失败: {e}")
            return False, str(e)

    def _set_system_time_direct(self, offset_seconds):
        """通过 Win32 API 直接设置系统时钟（需要 SeSystemtimePrivilege）"""
        if sys.platform != "win32":
            return False
        try:
            import ctypes
            from ctypes import wintypes

            TOKEN_ADJUST_PRIVILEGES = 0x0020
            TOKEN_QUERY = 0x0008
            SE_PRIVILEGE_ENABLED = 0x00000002

            class LUID(ctypes.Structure):
                _fields_ = [("LowPart", wintypes.DWORD), ("HighPart", wintypes.LONG)]

            class LUID_AND_ATTRIBUTES(ctypes.Structure):
                _fields_ = [("Luid", LUID), ("Attributes", wintypes.DWORD)]

            class TOKEN_PRIVILEGES(ctypes.Structure):
                _fields_ = [("PrivilegeCount", wintypes.DWORD), ("Privileges", LUID_AND_ATTRIBUTES * 1)]

            class SYSTEMTIME(ctypes.Structure):
                _fields_ = [
                    ("wYear", wintypes.WORD),
                    ("wMonth", wintypes.WORD),
                    ("wDayOfWeek", wintypes.WORD),
                    ("wDay", wintypes.WORD),
                    ("wHour", wintypes.WORD),
                    ("wMinute", wintypes.WORD),
                    ("wSecond", wintypes.WORD),
                    ("wMilliseconds", wintypes.WORD),
                ]

            kernel32 = ctypes.windll.kernel32
            advapi32 = ctypes.windll.advapi32

            # 1. 启用 SeSystemtimePrivilege
            token = wintypes.HANDLE()
            if not advapi32.OpenProcessToken(
                kernel32.GetCurrentProcess(),
                TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY,
                ctypes.byref(token)
            ):
                return False

            luid = LUID()
            if not advapi32.LookupPrivilegeValueW(None, "SeSystemtimePrivilege", ctypes.byref(luid)):
                kernel32.CloseHandle(token)
                return False

            tp = TOKEN_PRIVILEGES()
            tp.PrivilegeCount = 1
            tp.Privileges[0].Luid = luid
            tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED

            advapi32.AdjustTokenPrivileges(token, False, ctypes.byref(tp), 0, None, None)
            kernel32.CloseHandle(token)

            # 2. 设置系统时间
            target = datetime.now() + timedelta(seconds=offset_seconds)
            st = SYSTEMTIME()
            st.wYear = target.year
            st.wMonth = target.month
            st.wDay = target.day
            st.wHour = target.hour
            st.wMinute = target.minute
            st.wSecond = target.second
            st.wMilliseconds = int(target.microsecond / 1000)
            st.wDayOfWeek = (target.weekday() + 1) % 7

            result = kernel32.SetSystemTime(ctypes.byref(st))
            return result != 0
        except Exception:
            return False

    def _configure_w32time(self, ntp_server):
        """配置Windows时间服务：设置NTP服务器并触发立即同步"""
        if sys.platform != "win32":
            return False
        try:
            import subprocess
            # 配置Windows时间服务使用指定NTP服务器
            r1 = subprocess.run(
                [
                    "w32tm", "/config", "/manualpeerlist:" + ntp_server,
                    "/syncfromflags:manual", "/reliable:yes", "/update"
                ],
                capture_output=True, timeout=10
            )
            # 重启时间服务
            subprocess.run(["net", "stop", "w32time"], capture_output=True, timeout=10)
            subprocess.run(["net", "start", "w32time"], capture_output=True, timeout=10)
            # 触发立即同步
            r2 = subprocess.run(
                ["w32tm", "/resync"],
                capture_output=True, timeout=15
            )
            return r1.returncode == 0 and r2.returncode == 0
        except Exception:
            return False


# ====== 音频播放模块 ======
class AudioPlayer:
    """多区域音频播放器"""
    
    # 支持的音频格式
    SUPPORTED_FORMATS = {
        '.mp3': 'MP3',
        '.wav': 'WAV',
        '.ogg': 'OGG',
        '.m4a': 'M4A',
        '.aac': 'AAC',
        '.flac': 'FLAC',
        '.wma': 'WMA'
    }
    
    def __init__(self):
        self.zone_playing = {}  # zone_id -> bool
        self.zone_paused = {}   # zone_id -> bool
        self.global_paused = False
        self.zone_devices = {}  # zone_id -> device_index
        self.zone_volumes = {}  # zone_id -> float (0.0-1.0)
        self._pygame_inited = False
    
    def _init_pygame(self):
        if not self._pygame_inited:
            try:
                import pygame
                # 使用更兼容的音频设置
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=2048)
                self._pygame_inited = True
                logger.info("pygame音频初始化成功")
                return True
            except Exception as e:
                logger.error(f"pygame初始化失败: {e}")
                return False
        return True
    
    def check_audio_file(self, filepath):
        """检查音频文件是否有效"""
        if not os.path.exists(filepath):
            return False, "文件不存在"
        
        # 检查文件扩展名
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in self.SUPPORTED_FORMATS:
            return False, f"不支持的音频格式: {ext}，支持: {', '.join(self.SUPPORTED_FORMATS.keys())}"
        
        # 检查文件大小
        try:
            size = os.path.getsize(filepath)
            if size == 0:
                return False, "文件大小为0"
            if size < 1024:  # 小于1KB可能有问题
                logger.warning(f"音频文件较小: {filepath} ({size}字节)")
        except Exception as e:
            return False, f"无法读取文件: {e}"
        
        return True, "OK"
    
    def play(self, zone_id, filepath, volume=1.0, blocking=False):
        """在指定区域播放音频"""
        if self.global_paused:
            logger.info(f"全局暂停中，跳过区域{zone_id}播放")
            return False
        
        # 先检查文件
        ok, msg = self.check_audio_file(filepath)
        if not ok:
            logger.error(f"音频文件检查失败: {filepath} - {msg}")
            return False
        
        if not self._init_pygame():
            logger.error("pygame未初始化，无法播放")
            return False
        
        try:
            import pygame
            
            # 尝试加载音频文件
            try:
                sound = pygame.mixer.Sound(filepath)
            except Exception as e:
                logger.error(f"加载音频失败 {filepath}: {e}")
                # 尝试使用ffmpeg转换（如果可用）
                converted = self._try_convert_audio(filepath)
                if converted:
                    sound = pygame.mixer.Sound(converted)
                else:
                    return False
            
            # 设置音量（0.0-1.0）
            actual_volume = min(max(volume, 0.0), 1.0)
            sound.set_volume(actual_volume)
            
            # 播放
            channel = sound.play()
            
            self.zone_playing[zone_id] = True
            logger.info(f"区域{zone_id}播放: {os.path.basename(filepath)} 音量{actual_volume:.0%}")
            
            if blocking and channel:
                while channel.get_busy():
                    time.sleep(0.1)
            
            self.zone_playing[zone_id] = False
            return True
            
        except Exception as e:
            logger.error(f"播放失败 区域{zone_id}: {e}")
            self.zone_playing[zone_id] = False
            return False
    
    def _try_convert_audio(self, filepath):
        """尝试转换不支持的音频格式为WAV"""
        try:
            # 检查是否有ffmpeg
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
            if result.returncode != 0:
                return None
        except:
            logger.warning("未安装ffmpeg，无法转换音频格式")
            return None
        
        # 转换逻辑（可选实现）
        logger.info(f"尝试转换音频文件: {filepath}")
        return None  # 暂时返回None，后续可实现转换逻辑

    def stop_zone(self, zone_id):
        """停止指定区域"""
        try:
            import pygame
            pygame.mixer.stop()
            self.zone_playing[zone_id] = False
            logger.info(f"区域{zone_id}已停止")
        except Exception:
            pass

    def stop_all(self):
        """停止所有播放"""
        try:
            import pygame
            pygame.mixer.stop()
            self.zone_playing = {}
            logger.info("所有播放已停止")
        except Exception:
            pass

    def pause_global(self):
        """全局暂停"""
        self.global_paused = True
        self.stop_all()
        logger.info("全局已暂停")

    def resume_global(self):
        """全局恢复"""
        self.global_paused = False
        logger.info("全局已恢复")

    def pause_zone(self, zone_id):
        """暂停指定区域"""
        self.zone_paused[zone_id] = True
        self.stop_zone(zone_id)
        logger.info(f"区域{zone_id}已暂停")

    def resume_zone(self, zone_id):
        """恢复指定区域"""
        self.zone_paused[zone_id] = False
        logger.info(f"区域{zone_id}已恢复")

    def is_paused(self, zone_id):
        return self.zone_paused.get(zone_id, False) or self.global_paused

    def is_playing(self, zone_id):
        return self.zone_playing.get(zone_id, False)

    def is_global_paused(self):
        return self.global_paused

    def get_audio_devices(self):
        """获取系统音频输出设备列表"""
        devices = ["默认设备"]
        try:
            import pygame
            # pygame不直接支持设备枚举，用sounddevice
            try:
                import sounddevice as sd
                for i, dev in enumerate(sd.query_devices()):
                    if dev.get("max_output_channels", 0) > 0:
                        devices.append(f"{i}: {dev['name']}")
            except ImportError:
                pass
        except ImportError:
            pass
        return devices

    def set_volume(self, zone_id, volume):
        """设置区域音量"""
        self.zone_volumes[zone_id] = volume
        logger.info(f"区域{zone_id}音量设为{volume:.0%}")


# ====== 钉钉告警模块 ======
class DingTalkNotifier:
    """钉钉机器人异常告警"""

    def __init__(self):
        self.webhook = ""
        self.enabled = False
        self._last_alert = {}  # key -> timestamp，防止重复告警
        self._cooldown = 1800  # 30分钟内同一异常不重复

    def configure(self, webhook, enabled=True):
        self.webhook = webhook
        self.enabled = enabled

    def send(self, title, content, bypass_cooldown=False):
        """发送钉钉消息"""
        if not self.enabled or not self.webhook:
            return False

        # 冷却检查（测试时可绕过）
        key = f"{title}:{content[:50]}"
        now = time.time()
        if not bypass_cooldown and key in self._last_alert and now - self._last_alert[key] < self._cooldown:
            logger.debug(f"钉钉告警冷却中，跳过: {title}")
            return False

        try:
            data = json.dumps({
                "msgtype": "markdown",
                "markdown": {
                    "title": f"钢城智慧铃声-{title}",
                    "text": f"### 钢城智慧铃声系统 - {title}\n\n{content}\n\n> 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            }, ensure_ascii=False).encode("utf-8")

            req = urllib.request.Request(
                self.webhook,
                data=data,
                headers={"Content-Type": "application/json; charset=utf-8"}
            )
            resp = urllib.request.urlopen(req, timeout=10)
            result = json.loads(resp.read().decode("utf-8"))
            self._last_alert[key] = now
            logger.info(f"钉钉告警已发送: {title}")
            return result.get("errcode") == 0
        except Exception as e:
            logger.error(f"钉钉告警发送失败: {e}")
            return False

    def alert_bell_missed(self, zone_id, task_name, scheduled_time):
        """打铃异常：应该响没响"""
        self.send(
            "打铃异常",
            f"**区域**: {zone_id}\n\n**任务**: {task_name}\n\n**计划时间**: {scheduled_time}\n\n**异常**: 未按时响铃"
        )

    def alert_bell_unexpected(self, zone_id, task_name, scheduled_time):
        """打铃异常：不该响却响了"""
        self.send(
            "异常响铃",
            f"**区域**: {zone_id}\n\n**任务**: {task_name}\n\n**时间**: {scheduled_time}\n\n**异常**: 非计划响铃"
        )


# ====== 节假日查询模块 ======
class HolidayChecker:
    """中国节假日查询"""

    API_URL = "https://timor.tech/api/holiday/year/{}"

    def __init__(self):
        self.holidays = {}   # date_str -> name
        self.workdays = {}   # date_str -> name (调休上班)
        self._fetched_years = set()

    def fetch_year(self, year):
        """获取一年节假日数据"""
        if year in self._fetched_years:
            return True
        try:
            # 从数据库读取可配置的API地址
            from models import get_setting
            api_url = get_setting("holiday_api_url", "https://timor.tech/api/holiday/year/{}")
            url = api_url.format(year)
            req = urllib.request.Request(url, headers={"User-Agent": "SchoolBell/5.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read().decode("utf-8"))

            if data.get("code") == 0:
                for mmdd, info in data.get("holiday", {}).items():
                    full_date = f"{year}-{mmdd}"
                    name = info.get("name", "")
                    if info.get("holiday"):
                        self.holidays[full_date] = name
                    else:
                        self.workdays[full_date] = name
                self._fetched_years.add(year)
                logger.info(f"节假日数据获取成功: {year}年 {len(self.holidays)}个节假日")
                return True
        except Exception as e:
            logger.error(f"节假日API获取失败: {e}")
        return False

    def is_holiday(self, d):
        """判断某天是否为节假日（含周末）"""
        date_str = d.isoformat() if isinstance(d, date) else d
        d = date.fromisoformat(date_str) if isinstance(date_str, str) else d

        # 调休工作日优先
        if date_str in self.workdays:
            return False

        # 法定节假日
        if date_str in self.holidays:
            return True

        # 普通周末
        return d.weekday() >= 5

    def should_bell_today(self, d=None):
        """判断今天是否应该打铃"""
        if d is None:
            d = date.today()
        date_str = d.isoformat()

        # 调休工作日 = 要打铃
        if date_str in self.workdays:
            return True

        # 法定节假日 = 不打铃
        if date_str in self.holidays:
            return False

        # 普通周末 = 不打铃
        if d.weekday() >= 5:
            return False

        # 普通工作日 = 打铃
        return True

    def get_upcoming(self, days=30):
        """获取未来N天节假日"""
        result = []
        today = date.today()
        for i in range(1, days + 1):
            d = today + timedelta(days=i)
            date_str = d.isoformat()
            weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            if date_str in self.holidays:
                result.append({
                    "date": date_str,
                    "weekday": weekday_names[d.weekday()],
                    "name": self.holidays[date_str],
                    "type": "holiday",
                    "days_away": i
                })
            elif date_str in self.workdays:
                result.append({
                    "date": date_str,
                    "weekday": weekday_names[d.weekday()],
                    "name": self.workdays[date_str],
                    "type": "workday",
                    "days_away": i
                })
        return result

    def get_all_list(self, year=None):
        """获取全年节假日列表"""
        if year is None:
            year = date.today().year
        if year not in self._fetched_years:
            self.fetch_year(year)
        result = []
        prefix = f"{year}-"
        for d_str, name in self.holidays.items():
            if d_str.startswith(prefix):
                result.append({"date": d_str, "name": name, "type": "holiday"})
        for d_str, name in self.workdays.items():
            if d_str.startswith(prefix):
                result.append({"date": d_str, "name": name, "type": "workday"})
        return sorted(result, key=lambda x: x["date"])


# ====== 调度引擎 ======
class BellEngine:
    """核心调度引擎"""

    def __init__(self):
        self.player = AudioPlayer()
        self.ntp = NTPSync()
        self.dingtalk = DingTalkNotifier()
        self.holiday = HolidayChecker()
        self._bell_callbacks = []  # 打铃回调
        self._missed_bells = []    # 错过的打铃记录

    def on_bell(self, callback):
        """注册打铃回调"""
        self._bell_callbacks.append(callback)

    def _notify_bell(self, zone_id, bell_type, task_name, scheduled_time):
        """通知打铃事件"""
        for cb in self._bell_callbacks:
            try:
                cb(zone_id, bell_type, task_name, scheduled_time)
            except Exception:
                pass

    def check_and_ring(self):
        """检查并执行打铃（每秒调用一次）— 按区域独立判断"""
        from models import get_db

        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        weekday = now.weekday()  # 0=周一, 6=周日

        # 只在每分钟的第0秒触发
        if now.second != 0:
            return

        conn = get_db()
        zones = conn.execute("SELECT * FROM zones WHERE enabled=1 ORDER BY sort_order").fetchall()

        for zone in zones:
            zone_id = zone["id"]

            # 跳过全局暂停的区域
            if self.player.is_paused(zone_id):
                continue

            # 1. 检查今日例外（按区域）
            zone_override = self._get_zone_override(conn, today_str, zone_id)

            # 强制不打铃
            if zone_override == "force_no_ring":
                continue

            # 2. 判断今天是否应该打铃
            should_bell = self.holiday.should_bell_today()
            if not should_bell and zone_override != "force_ring":
                continue

            # 3. 获取该区域的课表
            schedule = self._get_zone_schedule(conn, zone, zone_override, today_str)
            if not schedule:
                continue

            # 4. 查找匹配的打铃任务
            tasks = conn.execute(
                "SELECT * FROM schedule_tasks WHERE schedule_id=? AND zone_id=? AND time=?",
                (schedule["id"], zone_id, current_time)
            ).fetchall()

            for task in tasks:
                # 正常模式检查days和一次性日期
                # force_ring模式：跳过日期约束，所有任务都执行
                if zone_override != "force_ring":
                    days = task["days"]
                    if days:
                        day_list = [int(d.strip()) for d in days.split(",") if d.strip()]
                        if (weekday + 1) not in day_list:
                            continue
                    if task["one_time_date"] and task["one_time_date"] != today_str:
                        continue

                # 5. 播放前自检铃声文件
                # 优先使用任务绑定的具体铃声文件
                bell_file = None
                if task["bell_id"]:
                    # 如果任务有关联的铃声文件，直接使用
                    row = conn.execute("SELECT filename FROM bells WHERE id=?", (task["bell_id"],)).fetchone()
                    if row:
                        bell_file = os.path.join("static", "sounds", row["filename"])
                
                # 如果没有bell_id或查找失败，使用bell_type查找
                if not bell_file:
                    bell_file = self._get_bell_file(conn, zone_id, task["bell_type"])
                if not bell_file:
                    bell_file = self._get_default_bell(task["bell_type"])

                if bell_file and os.path.exists(bell_file):
                    volume = self.player.zone_volumes.get(zone_id, zone["volume"])
                    threading.Thread(
                        target=self.player.play,
                        args=(zone_id, bell_file, volume),
                        daemon=True
                    ).start()

                    logger.info(f"🔔 打铃: {zone['name']}({zone_id}) {task['task_name']} {current_time}")
                    self._notify_bell(zone_id, task["bell_type"], task["task_name"], current_time)

                    from models import add_log
                    add_log("INFO", "bell", f"打铃: {zone['name']} {task['task_name']}", bell_file)
                else:
                    # 铃声文件缺失告警
                    logger.error(f"铃声文件缺失: {zone['name']}({zone_id}) {task['bell_type']}")
                    self.dingtalk.send(
                        "铃声文件缺失",
                        f"**区域**: {zone['name']}\n\n**任务**: {task['task_name']}\n\n**时间**: {current_time}\n\n**异常**: 铃声文件不存在"
                    )
                    from models import add_log
                    add_log("ERROR", "bell", f"铃声缺失: {zone['name']} {task['task_name']}", task["bell_type"])

        conn.close()

    def _get_zone_override(self, conn, date_str, zone_id):
        """获取某区域某日的覆盖状态: None=自动, force_ring, force_no_ring"""
        exc = conn.execute(
            "SELECT * FROM today_exceptions WHERE date=? AND zone_id=?",
            (date_str, zone_id)
        ).fetchone()
        if exc:
            return exc["action"]
        return None

    def _get_zone_schedule(self, conn, zone, zone_override, date_str):
        """获取区域当前应该使用的课表"""
        schedule_id = 0

        # 优先用今日覆盖指定的课表
        if zone_override == "force_ring":
            exc = conn.execute(
                "SELECT schedule_id FROM today_exceptions WHERE date=? AND zone_id=? AND action='force_ring'",
                (date_str, zone["id"])
            ).fetchone()
            if exc and exc["schedule_id"]:
                schedule_id = exc["schedule_id"]

        # 其次用区域绑定的默认课表
        if not schedule_id and zone["schedule_id"]:
            schedule_id = zone["schedule_id"]

        # 最后用全局激活课表
        if schedule_id:
            return conn.execute("SELECT * FROM schedules WHERE id=?", (schedule_id,)).fetchone()
        else:
            return conn.execute("SELECT * FROM schedules WHERE is_active=1").fetchone()

    def _get_bell_file(self, conn, zone_id, bell_type):
        """获取区域绑定的铃声文件"""
        row = conn.execute(
            "SELECT b.filename FROM bell_bindings bb JOIN bells b ON bb.bell_id=b.id WHERE bb.zone_id=? AND bb.bell_type=?",
            (zone_id, bell_type)
        ).fetchone()
        if row:
            return os.path.join("static", "sounds", row["filename"])
        return None

    def _get_default_bell(self, bell_type):
        """获取默认铃声文件"""
        default_map = {
            "class_start": "class_start.wav",
            "class_end": "class_end.wav",
            "prepare": "prepare.wav",
            "exercise": "exercise.wav",
            "lunch": "lunch.wav",
            "school_end": "school_end.wav",
            "emergency": "emergency.wav",
        }
        filename = default_map.get(bell_type, "class_start.wav")
        filepath = os.path.join("static", "sounds", filename)
        if os.path.exists(filepath):
            return filepath
        return None

    def manual_bell(self, zone_id, bell_type="class_start"):
        """手动打铃"""
        bell_file = self._get_default_bell(bell_type)
        if bell_file and os.path.exists(bell_file):
            volume = self.player.zone_volumes.get(zone_id, 0.8)
            threading.Thread(
                target=self.player.play,
                args=(zone_id, bell_file, volume),
                daemon=True
            ).start()
            from models import add_log
            add_log("INFO", "manual", f"手动打铃: 区域{zone_id} {bell_type}")
            return True
        return False

    def get_next_bell(self):
        """获取各区域的下次打铃时间，按时间排序"""
        from models import get_db

        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        weekday = now.weekday()

        conn = get_db()
        zones = conn.execute("SELECT * FROM zones WHERE enabled=1 ORDER BY sort_order").fetchall()

        results = []
        for zone in zones:
            zone_id = zone["id"]
            zone_override = self._get_zone_override(conn, today_str, zone_id)

            # force_no_ring: 今天不打铃
            if zone_override == "force_no_ring":
                results.append({
                    "zone_id": zone_id,
                    "zone_name": zone["name"],
                    "time": "--:--",
                    "name": "今日不打铃",
                    "bell_type": ""
                })
                continue

            should_bell = self.holiday.should_bell_today()
            if not should_bell and zone_override != "force_ring":
                tag = "假日/周末"
                if zone_override == "force_ring":
                    tag = "强制打铃"
                results.append({
                    "zone_id": zone_id,
                    "zone_name": zone["name"],
                    "time": "--:--",
                    "name": tag,
                    "bell_type": ""
                })
                continue

            schedule = self._get_zone_schedule(conn, zone, zone_override, today_str)
            if not schedule:
                results.append({
                    "zone_id": zone_id,
                    "zone_name": zone["name"],
                    "time": "--:--",
                    "name": "无课表",
                    "bell_type": ""
                })
                continue

            tasks = conn.execute(
                "SELECT * FROM schedule_tasks WHERE schedule_id=? AND zone_id=? AND time>=? ORDER BY time",
                (schedule["id"], zone_id, current_time)
            ).fetchall()

            found = False
            for task in tasks:
                # force_ring模式：跳过日期约束
                if zone_override != "force_ring":
                    days = task["days"]
                    if days:
                        day_list = [int(d.strip()) for d in days.split(",") if d.strip()]
                        if (weekday + 1) not in day_list:
                            continue
                results.append({
                    "zone_id": zone_id,
                    "zone_name": zone["name"],
                    "time": task["time"],
                    "name": task["task_name"],
                    "bell_type": task["bell_type"]
                })
                found = True
                break

            if not found:
                results.append({
                    "zone_id": zone_id,
                    "zone_name": zone["name"],
                    "time": "--:--",
                    "name": "今天已结束",
                    "bell_type": ""
                })

        conn.close()
        results.sort(key=lambda x: x["time"] if x["time"] != "--:--" else "99:99")
        return results

    def check_tomorrow_and_alert(self):
        """每日8:00检查明日状态，如非常规则发钉钉提醒"""
        from models import get_db

        tomorrow = date.today() + timedelta(days=1)
        tomorrow_str = tomorrow.isoformat()
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        tomorrow_weekday = weekday_names[tomorrow.weekday()]

        # 正常逻辑：工作日打铃，休息日不打铃
        should_bell_tomorrow = self.holiday.should_bell_today(tomorrow)

        conn = get_db()
        zones = conn.execute("SELECT * FROM zones WHERE enabled=1 ORDER BY sort_order").fetchall()

        alerts = []
        for zone in zones:
            zone_id = zone["id"]
            # 检查明日覆盖
            override = conn.execute(
                "SELECT * FROM tomorrow_overrides WHERE date=? AND zone_id=?",
                (tomorrow_str, zone_id)
            ).fetchone()

            # 检查今日覆盖是否影响明日（today_exceptions不影响明日）

            if override:
                action = override["action"]
                sched_id = override["schedule_id"] if "schedule_id" in override.keys() else 0
                sched_name = ""
                if sched_id:
                    s = conn.execute("SELECT name FROM schedules WHERE id=?", (sched_id,)).fetchone()
                    sched_name = s["name"] if s else ""

                if action == "force_ring" and not should_bell_tomorrow:
                    alerts.append(f"**{zone['name']}**: 明日({tomorrow_weekday})将执行打铃" +
                                  (f"，使用课表「{sched_name}」" if sched_name else ""))
                elif action == "force_no_ring" and should_bell_tomorrow:
                    alerts.append(f"**{zone['name']}**: 明日({tomorrow_weekday})将不执行打铃")

            # 即使没有覆盖，但明天是调休等特殊情况也提醒
            elif should_bell_tomorrow and tomorrow.weekday() >= 5:
                # 周末但要打铃（调休）
                alerts.append(f"**{zone['name']}**: 明日({tomorrow_weekday})为调休工作日，将正常打铃")
            elif not should_bell_tomorrow and tomorrow.weekday() < 5:
                # 工作日但不需要打铃（节假日）
                alerts.append(f"**{zone['name']}**: 明日({tomorrow_weekday})为节假日，将不打铃")

        # 附加上bell_schedules中明天的预约提醒（提前一天8:00提醒）
        bs_entries = conn.execute(
            "SELECT * FROM bell_schedules WHERE date=? AND remind_enabled=1",
            (tomorrow_str,)
        ).fetchall()
        for entry in bs_entries:
            zone = next((z for z in zones if z["id"] == entry["zone_id"]), None)
            zone_name = zone["name"] if zone else entry["zone_id"]
            action_text = "不打铃（关）" if entry["action"] == "force_no_ring" else "执行打铃（开）"
            sched_name = ""
            if entry["schedule_id"]:
                s = conn.execute("SELECT name FROM schedules WHERE id=?", (entry["schedule_id"],)).fetchone()
                sched_name = f"，课表「{s['name']}」" if s else ""
            reason = f"，原因：{entry['reason']}" if entry["reason"] else ""
            alerts.append(f"**{zone_name}** [预约]: {action_text}{sched_name}{reason}")

        conn.close()

        if alerts:
            content = f"**日期**: {tomorrow_str} {tomorrow_weekday}\n\n"
            content += "\n\n".join(alerts)
            content += "\n\n---\n如无需调整，请忽略此消息"
            self.dingtalk.send("明日状态提醒", content)

    def process_bell_schedules(self, mode="migrate"):
        """处理预约控制：mode='migrate'迁移今天预约到today_exceptions，mode='remind'发送提醒"""
        from models import get_db

        today_str = date.today().isoformat()
        tomorrow_str = (date.today() + timedelta(days=1)).isoformat()
        conn = get_db()

        if mode == "migrate":
            # 迁移今天的bell_schedules到today_exceptions
            entries = conn.execute(
                "SELECT * FROM bell_schedules WHERE date=?", (today_str,)
            ).fetchall()
            for entry in entries:
                zone_id = entry["zone_id"]
                # 检查是否已有today_exception（避免覆盖手动设置）
                existing = conn.execute(
                    "SELECT * FROM today_exceptions WHERE date=? AND zone_id=?",
                    (today_str, zone_id)
                ).fetchone()
                if not existing:
                    conn.execute(
                        "INSERT INTO today_exceptions (date, zone_id, action, reason, created_at, schedule_id) VALUES (?,?,?,?,?,?)",
                        (today_str, zone_id, entry["action"],
                         entry["reason"] or f"预约控制({entry['action']})",
                         entry["created_at"] or "",
                         entry["schedule_id"] or 0)
                    )
                    logger.info(f"预约控制迁移: {zone_id} {entry['action']} ({today_str})")
                    from models import add_log
                    add_log("INFO", "schedule", f"预约控制生效: {zone_id} {entry['action']} {today_str}")
            # 清理3天前的bell_schedules
            conn.execute("DELETE FROM bell_schedules WHERE date < date('now', '-3 days')")
            conn.commit()

        elif mode == "remind":
            # 检查明天是否有预约，发送提醒
            entries = conn.execute(
                "SELECT * FROM bell_schedules WHERE date=? AND remind_enabled=1 AND reminded=0",
                (tomorrow_str,)
            ).fetchall()

            if entries:
                weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                tomorrow_weekday = weekday_names[date.today().weekday() + 1 if date.today().weekday() < 6 else 0]
                zones = {z["id"]: z for z in conn.execute("SELECT * FROM zones").fetchall()}

                alerts = []
                for entry in entries:
                    zone_name = zones.get(entry["zone_id"], {}).get("name", entry["zone_id"])
                    action_text = "不打铃" if entry["action"] == "force_no_ring" else "执行打铃"
                    sched_name = ""
                    if entry["schedule_id"]:
                        s = conn.execute("SELECT name FROM schedules WHERE id=?", (entry["schedule_id"],)).fetchone()
                        sched_name = f"（课表：{s['name']}）" if s else ""
                    reason = f"，原因：{entry['reason']}" if entry["reason"] else ""
                    alerts.append(f"**{zone_name}**：{action_text}{sched_name}{reason}")

                content = f"**明日预约提醒**：{tomorrow_str} {tomorrow_weekday}\n\n"
                content += "\n\n".join(alerts)
                content += "\n\n---\n如需调整预约设置，请登录系统修改"
                self.dingtalk.send("预约铃声提醒", content)

                # 标记已提醒
                for entry in entries:
                    conn.execute(
                        "UPDATE bell_schedules SET reminded=1 WHERE id=?",
                        (entry["id"],)
                    )
                conn.commit()

        conn.close()

    def get_zone_status(self, zone_id, date_str=None):
        """获取某区域某天的完整状态"""
        from models import get_db

        if date_str is None:
            date_str = date.today().isoformat()

        d = date.fromisoformat(date_str)
        should_bell = self.holiday.should_bell_today(d)
        weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

        conn = get_db()
        zone = conn.execute("SELECT * FROM zones WHERE id=?", (zone_id,)).fetchone()
        if not zone:
            conn.close()
            return None

        # 检查覆盖
        override = conn.execute(
            "SELECT * FROM today_exceptions WHERE date=? AND zone_id=?",
            (date_str, zone_id)
        ).fetchone()

        schedule = self._get_zone_schedule(conn, zone, override["action"] if override else None, date_str)

        result = {
            "zone_id": zone_id,
            "zone_name": zone["name"],
            "date": date_str,
            "weekday": weekday_names[d.weekday()],
            "should_bell": should_bell,
            "override": override["action"] if override else None,
            "schedule_id": schedule["id"] if schedule else 0,
            "schedule_name": schedule["name"] if schedule else "无",
        }

        # 状态文字
        if result["override"] == "force_no_ring":
            result["status_text"] = "今日不打铃"
            result["status_type"] = "no_ring"
        elif result["override"] == "force_ring":
            result["status_text"] = "今日打铃" + (f"（{result['schedule_name']}）" if schedule else "")
            result["status_type"] = "ring"
        elif not should_bell:
            result["status_text"] = "休息日（不打铃）"
            result["status_type"] = "holiday"
        else:
            result["status_text"] = "正常打铃"
            result["status_type"] = "normal"

        conn.close()
        return result


# 全局引擎实例
engine = BellEngine()
